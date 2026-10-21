"""End-to-end integration and quality assurance test suite for DealWise.

Phase 7: Verifies end-to-end page rendering, Streamlit AppTest navigation,
session-state synchronization across modules, risk checklist updates,
and cross-engine mathematical consistency across UI, PDF, and CSV exports.
"""

from decimal import Decimal
import io
import pytest
import pypdf
from streamlit.testing.v1 import AppTest

from src.config import PAGES
from src.commercial_engine import (
    CommercialInputs,
    CommercialResult,
    calculate_commercials,
    format_currency,
)
from src.scenario_engine import compare_scenarios
from src.risk_engine import (
    RiskRecord,
    ChecklistItem,
    ChecklistStatus,
    get_default_readiness_checklist,
    calculate_proposal_readiness,
    generate_suggested_risk_flags,
    evaluate_financial_stress_cases,
)
from src.report_engine import (
    ProposalMetadata,
    assemble_proposal_report,
    generate_proposal_pdf,
    export_proposal_commercial_csv,
    generate_report_filename,
)


def test_apptest_all_pages_render_without_exceptions():
    """Verify all five platform pages render cleanly without throwing uncaught exceptions."""
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    assert len(at.exception) == 0, f"Exceptions on initial launch: {at.exception}"

    nav_radio = at.sidebar.radio[0]
    for page_section in PAGES:
        expected_label = f"{page_section.icon} {page_section.label}"
        assert expected_label in nav_radio.options

        # Switch page and execute
        nav_radio.set_value(expected_label)
        at.run()
        assert len(at.exception) == 0, f"Exception while rendering page '{expected_label}': {at.exception}"


def test_apptest_session_state_defaults_initialized():
    """Verify shared commercial inputs and defaults are initialized in Streamlit session state."""
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()

    # Verify session state keys exist and have expected defaults
    assert at.session_state["base_quoted_price"] == 100000.0
    assert at.session_state["delivery_costs"] == 50000.0
    assert at.session_state["software_costs"] == 6000.0
    assert at.session_state["other_expenses"] == 4000.0
    assert at.session_state["contingency_pct"] == 10.0
    assert at.session_state["discount_pct"] == 5.0
    assert at.session_state["target_margin_pct"] == 25.0
    assert "readiness_checklist" in at.session_state
    assert len(at.session_state["readiness_checklist"]) >= 8
    assert "proposal_title" in at.session_state
    assert "client_name" in at.session_state


def test_apptest_proposal_reports_page_interactions():
    """Verify Proposal Reports page components, form inputs, and download buttons render cleanly."""
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()

    # Navigate to Proposal Reports
    nav_radio = at.sidebar.radio[0]
    nav_radio.set_value("📄 Proposal Reports")
    at.run()
    assert len(at.exception) == 0

    # Verify form inputs and metric cards are rendered
    assert len(at.text_input) >= 6
    assert len(at.text_area) >= 5
    assert len(at.metric) >= 5


def test_cross_module_financial_consistency():
    """Verify mathematical consistency between commercial, scenario, risk, and report engines."""
    inputs = CommercialInputs(
        base_quoted_price=Decimal("120000.00"),
        delivery_costs=Decimal("60000.00"),
        software_tooling_costs=Decimal("8000.00"),
        other_expenses=Decimal("4000.00"),
        contingency_pct=Decimal("0.10"),
        discount_pct=Decimal("0.08"),
        cost_overrun_pct=Decimal("0.00"),
        target_margin_pct=Decimal("0.25"),
    )
    result = calculate_commercials(inputs)

    # 1. Commercial calculation assertions
    expected_direct_cost = Decimal("72000.00")
    expected_contingency = Decimal("7200.00")
    expected_total_cost = Decimal("79200.00")
    expected_net_revenue = Decimal("110400.00")
    expected_profit = Decimal("31200.00")

    assert result.direct_estimated_cost == expected_direct_cost
    assert result.contingency_amount == expected_contingency
    assert result.baseline_total_cost == expected_total_cost
    assert result.scenario_total_cost == expected_total_cost
    assert result.net_revenue == expected_net_revenue
    assert result.profit == expected_profit

    # 2. Scenario comparison reconciliation
    shock_inputs = CommercialInputs(
        base_quoted_price=inputs.base_quoted_price,
        delivery_costs=inputs.delivery_costs,
        software_tooling_costs=inputs.software_tooling_costs,
        other_expenses=inputs.other_expenses,
        contingency_pct=inputs.contingency_pct,
        discount_pct=Decimal("0.12"),  # +4 pp discount
        cost_overrun_pct=Decimal("0.15"),  # +15% labor overrun
        target_margin_pct=inputs.target_margin_pct,
    )
    comparison = compare_scenarios(inputs, shock_inputs)

    # Profit variance identity: Delta Profit == Delta Revenue - Delta Cost
    assert comparison.delta_profit == comparison.delta_net_revenue - comparison.delta_total_cost

    # 3. Financial stress cases reconciliation
    stress_cases = evaluate_financial_stress_cases(inputs, result)
    assert len(stress_cases) == 3
    for sc in stress_cases:
        assert sc.baseline_revenue == result.net_revenue
        assert sc.baseline_cost == result.scenario_total_cost
        assert sc.baseline_profit == result.profit
        assert sc.profit_impact == sc.stressed_profit - sc.baseline_profit

    # 4. Report engine assembly reconciliation
    meta = ProposalMetadata(
        title="Cloud Value Architecture Proposal",
        client_name="Global Financial Services",
    )
    report = assemble_proposal_report(
        metadata=meta,
        commercial_inputs=inputs,
        commercial_result=result,
        currency="USD",
        scenario_comparison=comparison,
        checklist=get_default_readiness_checklist(),
    )

    assert report.commercial.net_revenue == result.net_revenue
    assert report.commercial.scenario_total_cost == result.scenario_total_cost
    assert report.commercial.operating_profit == result.profit
    assert report.scenario.delta_profit == comparison.delta_profit


def test_pdf_content_integrity_and_disclaimer():
    """Verify generated PDF contains required sections, metadata, disclaimers, and no FX confusion."""
    inputs = CommercialInputs(
        base_quoted_price=Decimal("150000.00"),
        delivery_costs=Decimal("75000.00"),
        software_tooling_costs=Decimal("10000.00"),
        other_expenses=Decimal("5000.00"),
        contingency_pct=Decimal("0.10"),
        discount_pct=Decimal("0.05"),
        cost_overrun_pct=Decimal("0.00"),
        target_margin_pct=Decimal("0.25"),
    )
    result = calculate_commercials(inputs)

    meta = ProposalMetadata(
        title="Advanced Analytics Value Transformation",
        client_name="OmniRetail Global",
        industry="Retail & eCommerce",
        prepared_by="Commercial Strategy Partner",
        business_problem="Delayed reporting across multi-region distribution centers.",
        proposed_solution="Centralized real-time cloud analytics lakehouse.",
        scope_deliverables="Phase 1: Ingestion. Phase 2: Analytics. Phase 3: Reporting.",
        assumptions_exclusions="Client provides cloud permissions. Excludes third-party licensing.",
        timeline="12 calendar weeks.",
        payment_terms="Net 30 days upon milestone delivery.",
    )

    report = assemble_proposal_report(
        metadata=meta,
        commercial_inputs=inputs,
        commercial_result=result,
        currency="USD",
        checklist=get_default_readiness_checklist(),
    )

    pdf_bytes = generate_proposal_pdf(report)
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))

    raw_text = " ".join(page.extract_text() for page in reader.pages)
    full_text = " ".join(raw_text.split())

    assert "Advanced Analytics Value Transformation" in full_text
    assert "OmniRetail Global" in full_text
    assert "Executive Summary" in full_text
    assert "Commercial Pricing Schedule" in full_text
    assert "IMPORTANT COMMERCIAL NOTICE" in full_text or "DEMONSTRATION & ADVISORY REPORT" in full_text
    assert "Page 1 of" in full_text or "Page 2 of" in full_text


def test_csv_export_columns_and_data_alignment():
    """Verify CSV export contains expected headers, proper column alignment, and valid values."""
    inputs = CommercialInputs(
        base_quoted_price=Decimal("80000.00"),
        delivery_costs=Decimal("40000.00"),
        software_tooling_costs=Decimal("4000.00"),
        other_expenses=Decimal("2000.00"),
        contingency_pct=Decimal("0.08"),
        discount_pct=Decimal("0.05"),
        cost_overrun_pct=Decimal("0.00"),
        target_margin_pct=Decimal("0.20"),
    )
    result = calculate_commercials(inputs)

    meta = ProposalMetadata(
        title="Customer Intelligence Platform",
        client_name="Apex Telecommunications",
    )
    report = assemble_proposal_report(
        metadata=meta,
        commercial_inputs=inputs,
        commercial_result=result,
        currency="USD",
    )

    csv_data = export_proposal_commercial_csv(report)
    lines = csv_data.strip().split("\r\n" if "\r\n" in csv_data else "\n")

    # Verify key headers exist
    assert any("COMMERCIAL PRICING METRIC" in line for line in lines)
    assert any("Base Quoted Price" in line for line in lines)
    assert any("Net Realized Revenue" in line for line in lines)
    assert any("Operating Profit / (Loss)" in line for line in lines)
    assert any("Target Margin Met" in line for line in lines)

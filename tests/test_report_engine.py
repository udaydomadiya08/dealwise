"""Tests for proposal report engine, structured content assembly, and PDF/CSV deliverables.

Phase 6: Verifies report content assembly, input validation, financial reconciliation,
scenario integration, risk and readiness summaries, ReportLab PDF generation,
and spreadsheet CSV exports.
"""

from decimal import Decimal, ROUND_HALF_UP
import io
import pytest
import pypdf

from src.commercial_engine import (
    CommercialInputs,
    CommercialResult,
    calculate_commercials,
)
from src.scenario_engine import (
    compare_scenarios,
)
from src.risk_engine import (
    RiskRecord,
    ChecklistItem,
    ChecklistStatus,
    get_default_readiness_checklist,
    generate_suggested_risk_flags,
)
from src.report_engine import (
    ProposalMetadata,
    CommercialScheduleData,
    ScenarioSummaryData,
    RiskSummaryData,
    ProposalReportContent,
    assemble_commercial_schedule,
    assemble_scenario_summary,
    assemble_risk_summary,
    assemble_proposal_report,
    generate_proposal_pdf,
    export_proposal_commercial_csv,
    generate_report_filename,
)


@pytest.fixture
def sample_commercial_inputs() -> CommercialInputs:
    """Standard baseline commercial inputs for testing."""
    return CommercialInputs(
        base_quoted_price=Decimal("100000.00"),
        delivery_costs=Decimal("50000.00"),
        software_tooling_costs=Decimal("5000.00"),
        other_expenses=Decimal("5000.00"),
        contingency_pct=Decimal("0.10"),
        discount_pct=Decimal("0.05"),
        cost_overrun_pct=Decimal("0.00"),
        target_margin_pct=Decimal("0.25"),
    )


@pytest.fixture
def sample_commercial_result(sample_commercial_inputs: CommercialInputs) -> CommercialResult:
    """Standard baseline commercial engine outputs."""
    return calculate_commercials(sample_commercial_inputs)


@pytest.fixture
def sample_metadata() -> ProposalMetadata:
    """Realistic consulting proposal metadata."""
    return ProposalMetadata(
        title="Enterprise Data Platform Architecture",
        client_name="Global Logistics Corp",
        industry="Supply Chain & Transportation",
        prepared_by="Data Practice Commercial Lead",
        date_str="October 21, 2026",
        business_problem="Client suffers from siloed legacy warehouse data with 48-hour reporting delay.",
        proposed_solution="Deploy real-time ingestion lakehouse with automated margin analytics.",
        scope_deliverables="Phase 1: Ingestion Pipelines. Phase 2: Analytics Marts. Phase 3: Executive Dashboards.",
        assumptions_exclusions="Client provides AWS IAM credentials. Excludes legacy database license fees.",
        timeline="10 calendar weeks across 3 delivery sprints.",
        payment_terms="30% on kickoff, 40% on milestone 2, 30% upon final acceptance.",
        notes_and_next_steps="Review commercial schedule with client procurement before submission.",
        is_hypothetical_demo=True,
    )


def test_proposal_metadata_validation(sample_metadata: ProposalMetadata):
    """Verify validation returns empty warnings for complete metadata and catches incomplete fields."""
    warnings = sample_metadata.validate()
    assert warnings == []

    # Incomplete metadata
    empty_meta = ProposalMetadata(
        title="",
        client_name="",
        business_problem="Not provided",
        proposed_solution="Not provided",
        scope_deliverables="Not provided",
        timeline="Not provided",
        payment_terms="Not provided",
    )
    warns = empty_meta.validate()
    assert len(warns) >= 5
    assert any("title" in w.lower() for w in warns)
    assert any("client" in w.lower() for w in warns)
    assert any("business problem" in w.lower() for w in warns)
    assert any("payment terms" in w.lower() for w in warns)


def test_assemble_commercial_schedule(
    sample_commercial_inputs: CommercialInputs,
    sample_commercial_result: CommercialResult,
):
    """Verify commercial schedule data accurately reconciles with engine outputs."""
    sched = assemble_commercial_schedule(
        sample_commercial_inputs,
        sample_commercial_result,
        currency="USD",
    )
    assert sched.currency == "USD"
    assert sched.base_quoted_price == Decimal("100000.00")
    assert sched.net_revenue == Decimal("95000.00")
    assert sched.direct_estimated_cost == Decimal("60000.00")
    assert sched.contingency_amount == Decimal("6000.00")
    assert sched.baseline_total_cost == Decimal("66000.00")
    assert sched.scenario_total_cost == Decimal("66000.00")
    assert sched.operating_profit == Decimal("29000.00")
    assert sched.profit_margin_pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal("30.53")
    assert sched.meets_target_margin is True
    assert sched.is_profitable is True


def test_assemble_scenario_summary(sample_commercial_inputs: CommercialInputs):
    """Verify scenario summary maps delta metrics and handles None gracefully."""
    # When scenario is None
    assert assemble_scenario_summary(None) is None

    # When scenario is evaluated
    shock_inputs = CommercialInputs(
        base_quoted_price=sample_commercial_inputs.base_quoted_price,
        delivery_costs=sample_commercial_inputs.delivery_costs,
        software_tooling_costs=sample_commercial_inputs.software_tooling_costs,
        other_expenses=sample_commercial_inputs.other_expenses,
        contingency_pct=sample_commercial_inputs.contingency_pct,
        discount_pct=Decimal("0.15"),  # Increased discount
        cost_overrun_pct=Decimal("0.20"),  # Increased overrun
        target_margin_pct=sample_commercial_inputs.target_margin_pct,
    )
    comparison = compare_scenarios(sample_commercial_inputs, shock_inputs)
    scen_summary = assemble_scenario_summary(comparison)

    assert scen_summary is not None
    assert scen_summary.baseline_revenue == Decimal("95000.00")
    assert scen_summary.scenario_revenue == Decimal("85000.00")
    assert scen_summary.delta_revenue == Decimal("-10000.00")
    assert scen_summary.baseline_cost == Decimal("66000.00")
    assert scen_summary.scenario_cost == Decimal("76000.00")
    assert scen_summary.delta_cost == Decimal("10000.00")
    assert scen_summary.delta_profit == Decimal("-20000.00")
    assert scen_summary.delta_margin_pp.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal("-19.94")


def test_assemble_risk_summary():
    """Verify risk and readiness summary extracts open counts and unresolved items."""
    checklist = get_default_readiness_checklist()
    risks = [
        RiskRecord(
            risk_id="RSK-01",
            category="Scope",
            description="Scope creep in ETL",
            likelihood=4,
            impact=4,
            owner="Architect",
            mitigation="Scope freeze",
            status="Open",
        ),
        RiskRecord(
            risk_id="RSK-02",
            category="Commercial",
            description="Client discount pressure",
            likelihood=2,
            impact=2,
            owner="Partner",
            mitigation="Hold price",
            status="Mitigated",
        ),
    ]

    risk_data = assemble_risk_summary(risks, checklist)
    assert risk_data.open_risks_count == 1
    assert risk_data.critical_risks_count == 1  # 4 * 4 = 16 (Critical)
    assert len(risk_data.prioritized_risks) == 2
    assert len(risk_data.unresolved_items) > 0
    assert len(risk_data.mitigation_actions) == 1  # Mitigated risk excluded from active plan


def test_assemble_proposal_report_full(
    sample_metadata: ProposalMetadata,
    sample_commercial_inputs: CommercialInputs,
    sample_commercial_result: CommercialResult,
):
    """Verify end-to-end report data assembly and dictionary representation."""
    report = assemble_proposal_report(
        metadata=sample_metadata,
        commercial_inputs=sample_commercial_inputs,
        commercial_result=sample_commercial_result,
        currency="USD",
        risks=[],
        checklist=get_default_readiness_checklist(),
    )
    assert report.metadata.title == "Enterprise Data Platform Architecture"
    assert report.commercial.net_revenue == Decimal("95000.00")
    assert "DEMONSTRATION & ADVISORY REPORT" in report.disclaimer_text
    assert "Methodology" in report.methodology_notes
    assert len(report.validation_warnings) == 0

    d = report.to_dict()
    assert d["net_revenue"] == 95000.0
    assert d["operating_profit"] == 29000.0
    assert d["profit_margin_pct"] == 30.53
    assert d["meets_target_margin"] is True


def test_pdf_generation_produces_valid_bytes(
    sample_metadata: ProposalMetadata,
    sample_commercial_inputs: CommercialInputs,
    sample_commercial_result: CommercialResult,
):
    """Verify ReportLab PDF generation outputs valid, non-empty PDF bytes starting with %PDF-."""
    checklist = get_default_readiness_checklist()
    risks = generate_suggested_risk_flags(sample_commercial_inputs, sample_commercial_result)

    report = assemble_proposal_report(
        metadata=sample_metadata,
        commercial_inputs=sample_commercial_inputs,
        commercial_result=sample_commercial_result,
        currency="USD",
        risks=risks,
        checklist=checklist,
    )

    pdf_bytes = generate_proposal_pdf(report)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF-")


def test_pdf_text_extraction_and_sections(
    sample_metadata: ProposalMetadata,
    sample_commercial_inputs: CommercialInputs,
    sample_commercial_result: CommercialResult,
):
    """Verify PDF contains required section headings, title, client, and disclaimers using pypdf."""
    checklist = get_default_readiness_checklist()
    risks = generate_suggested_risk_flags(sample_commercial_inputs, sample_commercial_result)

    shock_inputs = CommercialInputs(
        base_quoted_price=sample_commercial_inputs.base_quoted_price,
        delivery_costs=sample_commercial_inputs.delivery_costs,
        software_tooling_costs=sample_commercial_inputs.software_tooling_costs,
        other_expenses=sample_commercial_inputs.other_expenses,
        contingency_pct=sample_commercial_inputs.contingency_pct,
        discount_pct=Decimal("0.10"),
        cost_overrun_pct=Decimal("0.15"),
        target_margin_pct=sample_commercial_inputs.target_margin_pct,
    )
    scen_comp = compare_scenarios(sample_commercial_inputs, shock_inputs)

    report = assemble_proposal_report(
        metadata=sample_metadata,
        commercial_inputs=sample_commercial_inputs,
        commercial_result=sample_commercial_result,
        currency="USD",
        scenario_comparison=scen_comp,
        risks=risks,
        checklist=checklist,
    )

    pdf_bytes = generate_proposal_pdf(report)
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    num_pages = len(reader.pages)
    assert num_pages >= 2

    # Extract all text across pages
    full_text = " ".join(page.extract_text() for page in reader.pages)

    # Assert major elements exist in extracted text
    assert "Enterprise Data Platform Architecture" in full_text
    assert "Global Logistics Corp" in full_text
    assert "Executive Summary" in full_text
    assert "Commercial Pricing Schedule" in full_text
    assert "What-If Scenario" in full_text
    assert "Commercial Risk Intelligence" in full_text
    assert "IMPORTANT COMMERCIAL NOTICE" in full_text or "DEMONSTRATION & ADVISORY REPORT" in full_text
    assert "Page" in full_text


def test_pdf_long_content_and_multi_page_resilience(
    sample_commercial_inputs: CommercialInputs,
    sample_commercial_result: CommercialResult,
):
    """Verify PDF generator handles very long descriptions and tables across pages without crashing."""
    long_desc = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 30
    long_meta = ProposalMetadata(
        title="Enterprise Complex Multi-Year Transformation Proposal",
        client_name="Global Conglomerate Corporation International",
        industry="Heavy Manufacturing, Utilities & Energy Systems",
        prepared_by="Strategic Commercial Operations Lead",
        business_problem=long_desc,
        proposed_solution=long_desc,
        scope_deliverables=long_desc,
        assumptions_exclusions=long_desc,
        timeline="24 calendar months across 8 distinct phases.",
        payment_terms="Quarterly retrospective payments tied to milestone sign-offs.",
        notes_and_next_steps=long_desc,
    )

    # 10 risks to ensure table pagination resilience
    many_risks = [
        RiskRecord(
            risk_id=f"RSK-LONG-{i:02d}",
            category="Delivery",
            description=f"Multi-system integration friction across operational environment {i}",
            likelihood=(i % 5) + 1,
            impact=((i + 2) % 5) + 1,
            owner=f"Lead Architect {i}",
            mitigation=f"Deploy automated regression test suite {i}",
            status="Open",
        )
        for i in range(1, 11)
    ]

    report = assemble_proposal_report(
        metadata=long_meta,
        commercial_inputs=sample_commercial_inputs,
        commercial_result=sample_commercial_result,
        currency="USD",
        risks=many_risks,
        checklist=get_default_readiness_checklist(),
    )

    pdf_bytes = generate_proposal_pdf(report)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")

    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) >= 3


def test_currency_formatting_consistency_in_pdf(
    sample_metadata: ProposalMetadata,
    sample_commercial_inputs: CommercialInputs,
    sample_commercial_result: CommercialResult,
):
    """Verify currency labels (USD vs INR) are preserved and do not cause errors."""
    for curr in ("USD", "INR"):
        report = assemble_proposal_report(
            metadata=sample_metadata,
            commercial_inputs=sample_commercial_inputs,
            commercial_result=sample_commercial_result,
            currency=curr,
            risks=[],
            checklist=[],
        )
        pdf_bytes = generate_proposal_pdf(report)
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b"%PDF-")
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        full_text = " ".join(page.extract_text() for page in reader.pages)
        assert curr in full_text


def test_report_filename_generator():
    """Verify filename generator produces clean, safe names without dangerous characters."""
    fname = generate_report_filename("Cloud Data Platform / Scoping: Phase 1!", "Acme Corp & Co.")
    assert fname.startswith("dealwise_proposal_acme_corp_co_cloud_data_platform_scoping")
    assert fname.endswith(".pdf")
    assert "/" not in fname
    assert ":" not in fname
    assert "!" not in fname
    assert "&" not in fname


def test_export_proposal_commercial_csv(
    sample_metadata: ProposalMetadata,
    sample_commercial_inputs: CommercialInputs,
    sample_commercial_result: CommercialResult,
):
    """Verify CSV export contains header metadata, commercial rows, and scenario comparisons."""
    shock_inputs = CommercialInputs(
        base_quoted_price=sample_commercial_inputs.base_quoted_price,
        delivery_costs=sample_commercial_inputs.delivery_costs,
        software_tooling_costs=sample_commercial_inputs.software_tooling_costs,
        other_expenses=sample_commercial_inputs.other_expenses,
        contingency_pct=sample_commercial_inputs.contingency_pct,
        discount_pct=Decimal("0.10"),
        cost_overrun_pct=Decimal("0.15"),
        target_margin_pct=sample_commercial_inputs.target_margin_pct,
    )
    scen_comp = compare_scenarios(sample_commercial_inputs, shock_inputs)

    report = assemble_proposal_report(
        metadata=sample_metadata,
        commercial_inputs=sample_commercial_inputs,
        commercial_result=sample_commercial_result,
        currency="USD",
        scenario_comparison=scen_comp,
    )

    csv_text = export_proposal_commercial_csv(report)
    assert "DEALWISE PROPOSAL COMMERCIAL BRIEF" in csv_text
    assert "Global Logistics Corp" in csv_text
    assert "Base Quoted Price,100000.00,USD" in csv_text
    assert "Net Realized Revenue,95000.00,USD" in csv_text
    assert "Operating Profit / (Loss),29000.00,USD" in csv_text
    assert "SCENARIO COMPARISON METRIC" in csv_text
    assert "Net Revenue,95000.00,90000.00,-5000.00" in csv_text

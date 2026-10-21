"""Tests for Infosys-aligned real-world consulting case study mode and data provenance."""

import io
from decimal import Decimal
import pypdf
import pytest
from streamlit.testing.v1 import AppTest

from src.case_study import (
    OFFICIAL_INFOSYS_SOURCES,
    INFOSYS_CASE_STUDY_PRESET,
    VerifiedPublicFact,
    get_case_study_preset,
)
from src.commercial_engine import calculate_commercials, CommercialInputs
from src.report_engine import (
    ProposalMetadata,
    assemble_proposal_report,
    generate_proposal_pdf,
    export_proposal_commercial_csv,
)
from src.risk_engine import get_default_readiness_checklist


def test_official_infosys_sources_provenance():
    """Verify that all official Infosys sources have valid metadata, URLs, and claims."""
    assert len(OFFICIAL_INFOSYS_SOURCES) >= 6

    expected_categories = {
        "Strategy & Services",
        "Technology Platforms",
        "Financial Benchmark",
        "Industry Verticals",
    }
    found_categories = {s.category for s in OFFICIAL_INFOSYS_SOURCES}
    assert expected_categories.issubset(found_categories)

    for src in OFFICIAL_INFOSYS_SOURCES:
        assert isinstance(src, VerifiedPublicFact)
        assert src.source_url.startswith("https://www.infosys.com")
        assert len(src.topic.strip()) > 0
        assert len(src.official_source_title.strip()) > 0
        assert len(src.retrieval_date.strip()) > 0
        assert len(src.claims_supported) > 0
        # Ensure no placeholder or fabricated claims
        assert "not provided" not in src.fact_summary.lower()


def test_infosys_case_study_preset_structure():
    """Verify preset structure, duration, pyramid, and risk records."""
    preset = get_case_study_preset("infosys_cloud_ai_transformation")
    assert preset.case_id == "infosys_cloud_ai_transformation"
    assert "Global OmniRetail" in preset.client_name
    assert preset.duration_weeks == 36
    assert len(preset.staffing_pyramid) == 6
    assert len(preset.risks) == 5
    assert len(preset.checklist_statuses) == 9

    # Verify staffing pyramid total FTEs
    total_ftes = sum(r.count_fte for r in preset.staffing_pyramid)
    assert total_ftes == 13

    # Verify risk severity and financial exposures
    for r in preset.risks:
        assert 1 <= r.likelihood <= 5
        assert 1 <= r.impact <= 5
        assert r.score == r.likelihood * r.impact
        assert r.financial_exposure is not None and r.financial_exposure > Decimal("0")


def test_case_study_commercial_math_and_target_alignment():
    """Verify exact commercial calculation outputs for the case study baseline."""
    preset = INFOSYS_CASE_STUDY_PRESET
    inputs = preset.inputs
    result = calculate_commercials(inputs)

    # Base price: $1,250,000, 5% discount -> Net Revenue: $1,187,500.00
    assert result.net_revenue == Decimal("1187500.00")

    # Direct costs: $780,000 + $85,000 + $35,000 = $900,000.00
    assert result.direct_estimated_cost == Decimal("900000.00")

    # Contingency: 6.25% of $900,000 = $56,250.00
    assert result.contingency_amount == Decimal("56250.00")
    assert result.baseline_total_cost == Decimal("956250.00")

    # Overrun: 10% on $780,000 labor = $78,000.00
    # Scenario total cost: $956,250 + $78,000 = $1,034,250.00
    assert result.scenario_total_cost == Decimal("1034250.00")

    # Profit: $1,187,500 - $1,034,250 = $153,250.00
    assert result.profit == Decimal("153250.00")
    assert result.is_profitable is True

    # Target Margin: 21.0% (Infosys corporate operating margin benchmark)
    assert inputs.target_margin_pct == Decimal("0.21")


def test_case_study_pdf_generation_and_text_extraction():
    """Verify PDF generation includes case study context, verified sources, and disclaimers."""
    preset = INFOSYS_CASE_STUDY_PRESET
    inputs = preset.inputs
    result = calculate_commercials(inputs)

    sources_dict = [
        {
            "topic": s.topic,
            "official_source_title": s.official_source_title,
            "source_url": s.source_url,
            "retrieval_date": s.retrieval_date,
            "category": s.category,
        }
        for s in OFFICIAL_INFOSYS_SOURCES
    ]

    meta = ProposalMetadata(
        title=preset.title,
        client_name=preset.client_name,
        industry=preset.industry,
        prepared_by=preset.provider_context,
        business_problem=preset.business_problem,
        proposed_solution=preset.proposed_solution,
        scope_deliverables=preset.scope_deliverables,
        assumptions_exclusions=preset.assumptions_exclusions,
        timeline=preset.delivery_timeline,
        payment_terms=preset.payment_terms,
        notes_and_next_steps=preset.executive_recommendation,
        case_study_name="Infosys: Enterprise Cloud & AI Transformation",
        provider_context=preset.provider_context,
        executive_recommendation=preset.executive_recommendation,
        sources_register=sources_dict,
    )

    content = assemble_proposal_report(
        metadata=meta,
        commercial_inputs=inputs,
        commercial_result=result,
        currency="USD",
        risks=preset.risks,
        checklist=get_default_readiness_checklist(),
    )

    pdf_bytes = generate_proposal_pdf(content)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")

    # Extract text using pypdf
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    all_text = " ".join(page.extract_text() for page in reader.pages)

    assert "REAL-WORLD CASE STUDY CONTEXT" in all_text
    assert "Global OmniRetail Enterprises" in all_text
    assert "Cobalt" in all_text
    assert "Topaz" in all_text
    assert "Verified Company Disclosures" in all_text
    assert "https://www.infosys.com" in all_text
    assert "EXECUTIVE COMMERCIAL RECOMMENDATION" in all_text


def test_case_study_csv_export_format():
    """Verify CSV export includes provider reference, recommendation, and sources register."""
    preset = INFOSYS_CASE_STUDY_PRESET
    inputs = preset.inputs
    result = calculate_commercials(inputs)

    sources_dict = [
        {
            "topic": s.topic,
            "official_source_title": s.official_source_title,
            "source_url": s.source_url,
            "retrieval_date": s.retrieval_date,
            "category": s.category,
        }
        for s in OFFICIAL_INFOSYS_SOURCES
    ]

    meta = ProposalMetadata(
        title=preset.title,
        client_name=preset.client_name,
        industry=preset.industry,
        prepared_by=preset.provider_context,
        case_study_name="Infosys: Enterprise Cloud & AI Transformation",
        provider_context=preset.provider_context,
        executive_recommendation=preset.executive_recommendation,
        sources_register=sources_dict,
    )

    content = assemble_proposal_report(
        metadata=meta,
        commercial_inputs=inputs,
        commercial_result=result,
        currency="USD",
    )

    csv_text = export_proposal_commercial_csv(content)
    assert "Case Study Identifier,Infosys: Enterprise Cloud & AI Transformation" in csv_text
    assert "Provider Reference,Infosys Consulting" in csv_text
    assert "VERIFIED PUBLIC SOURCES & DATA PROVENANCE (OFFICIAL DISCLOSURES)" in csv_text
    assert "Infosys Cobalt" in csv_text
    assert "Infosys Topaz" in csv_text
    assert "https://www.infosys.com/services/consulting/overview.html" in csv_text


def test_apptest_case_study_mode_toggle_and_rendering():
    """Verify Streamlit AppTest switches to case study mode cleanly without exceptions."""
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    assert not at.exception

    # Initially in Standard workspace
    assert at.session_state["base_quoted_price"] == 100000.0

    # Select Infosys Case Study in sidebar
    # Find sidebar selectbox with label "Scenario Mode"
    scenario_sel = next(
        (sb for sb in at.sidebar.selectbox if "Scenario Mode" in sb.label),
        None,
    )
    assert scenario_sel is not None

    # Select the second option
    scenario_sel.select("Infosys: Enterprise Cloud & AI Transformation")
    at.run()
    assert not at.exception

    # Verify session state was populated with case study preset parameters
    assert at.session_state["case_study_active"] is True
    assert at.session_state["base_quoted_price"] == 1250000.0
    assert at.session_state["target_margin_pct"] == 21.0
    assert at.session_state["client_name"] == "Global OmniRetail Enterprises"
    assert "Cobalt & Topaz" in at.session_state["proposal_title"]

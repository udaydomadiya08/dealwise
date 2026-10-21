"""Deployment smoke test and rapid health check suite for DealWise.

Phase 7: Verifies syntax, module importability, core engine execution,
PDF compilation, and deployment readiness in under 1 second.
"""

from decimal import Decimal
import py_compile
import pytest

from src.config import APP_TITLE, APP_VERSION, PAGES, get_navigation_map
from src.commercial_engine import CommercialInputs, calculate_commercials
from src.scenario_engine import compare_scenarios
from src.risk_engine import get_default_readiness_checklist, calculate_proposal_readiness
from src.report_engine import (
    ProposalMetadata,
    assemble_proposal_report,
    generate_proposal_pdf,
)


def test_smoke_syntax_check():
    """Verify that all core application files compile with valid Python syntax."""
    py_compile.compile("app.py", doraise=True)
    py_compile.compile("src/config.py", doraise=True)
    py_compile.compile("src/commercial_engine.py", doraise=True)
    py_compile.compile("src/dashboard.py", doraise=True)
    py_compile.compile("src/scenario_engine.py", doraise=True)
    py_compile.compile("src/risk_engine.py", doraise=True)
    py_compile.compile("src/report_engine.py", doraise=True)
    py_compile.compile("src/case_study.py", doraise=True)


def test_smoke_config_integrity():
    """Verify configuration metadata, active pages, and navigation map."""
    assert APP_TITLE == "DealWise"
    assert "0.6.0" in APP_VERSION or "0.7.0" in APP_VERSION
    assert len(PAGES) == 5
    assert all(p.is_active for p in PAGES)
    nav_map = get_navigation_map()
    assert len(nav_map) == 5


def test_smoke_commercial_engine():
    """Verify commercial calculation engine executes cleanly with Decimal output."""
    inputs = CommercialInputs.from_percentages(
        base_quoted_price=100000.0,
        delivery_costs=50000.0,
        software_tooling_costs=5000.0,
        other_expenses=5000.0,
        contingency_pct=10.0,
        discount_pct=5.0,
        cost_overrun_pct=0.0,
        target_margin_pct=25.0,
    )
    result = calculate_commercials(inputs)
    assert result.net_revenue == Decimal("95000.00")
    assert result.scenario_total_cost == Decimal("66000.00")
    assert result.profit == Decimal("29000.00")
    assert result.is_profitable is True


def test_smoke_pdf_generation():
    """Verify ReportLab in-memory PDF compiles without errors."""
    inputs = CommercialInputs.from_percentages(
        base_quoted_price=100000.0,
        delivery_costs=50000.0,
        software_tooling_costs=5000.0,
        other_expenses=5000.0,
        contingency_pct=10.0,
        discount_pct=5.0,
        cost_overrun_pct=0.0,
        target_margin_pct=25.0,
    )
    result = calculate_commercials(inputs)
    meta = ProposalMetadata(title="Smoke Test Proposal", client_name="Acme Corp")
    report = assemble_proposal_report(
        metadata=meta,
        commercial_inputs=inputs,
        commercial_result=result,
        currency="USD",
        checklist=get_default_readiness_checklist(),
    )
    pdf_bytes = generate_proposal_pdf(report)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")

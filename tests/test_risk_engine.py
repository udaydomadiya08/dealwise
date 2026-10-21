"""Unit tests for Phase 5 Commercial Risk Intelligence Engine."""

from decimal import Decimal
import pytest

from src.commercial_engine import CommercialInputs, calculate_commercials
from src.risk_engine import (
    RiskRecord,
    RiskSeverity,
    ChecklistItem,
    ChecklistStatus,
    RiskValidationError,
    calculate_risk_score,
    get_risk_severity,
    prioritize_risks,
    calculate_proposal_readiness,
    get_default_readiness_checklist,
    evaluate_financial_stress_cases,
    generate_suggested_risk_flags,
    generate_mitigation_plan,
    export_risk_assessment_csv,
)


@pytest.fixture
def baseline_inputs():
    """Standard profitable advisory engagement baseline."""
    return CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="50000.00",
        software_tooling_costs="6000.00",
        other_expenses="4000.00",
        contingency_pct="0.10",
        discount_pct="0.05",
        cost_overrun_pct="0.00",
        target_margin_pct="0.25",
    )


# 1. Risk-score calculation
def test_risk_score_calculation():
    """Verify ordinal risk score calculation formula (L x I)."""
    assert calculate_risk_score(1, 1) == 1
    assert calculate_risk_score(3, 4) == 12
    assert calculate_risk_score(5, 5) == 25


# 2. Each severity band and its boundaries
@pytest.mark.parametrize(
    "score,expected_severity",
    [
        (1, RiskSeverity.LOW),
        (4, RiskSeverity.LOW),
        (5, RiskSeverity.MODERATE),
        (9, RiskSeverity.MODERATE),
        (10, RiskSeverity.HIGH),
        (14, RiskSeverity.HIGH),
        (15, RiskSeverity.CRITICAL),
        (25, RiskSeverity.CRITICAL),
    ],
)
def test_severity_bands_and_boundaries(score, expected_severity):
    """Verify exact boundary mappings for Low, Moderate, High, and Critical bands."""
    assert get_risk_severity(score) == expected_severity


# 3. Invalid likelihood and impact values
@pytest.mark.parametrize(
    "likelihood,impact",
    [
        (0, 3),
        (6, 3),
        (3, 0),
        (3, 6),
        (-1, 2),
        (2, -1),
        (True, 3),   # bool rejected
        (3, False),  # bool rejected
        ("3", 3),    # string rejected
        (3.5, 4),    # float rejected
    ],
)
def test_invalid_likelihood_and_impact(likelihood, impact):
    """Ensure out-of-range, non-integer, and boolean score inputs are strictly rejected."""
    with pytest.raises(RiskValidationError):
        calculate_risk_score(likelihood, impact)


# 4. Risk-record validation
def test_risk_record_validation():
    """Verify validation of RiskRecord fields."""
    # Valid record
    record = RiskRecord(
        risk_id="RSK-001",
        category="Scope & Delivery",
        description="Delivery scope ambiguity",
        likelihood=3,
        impact=4,
        owner="Engagement Manager",
        mitigation="Define statement of work",
        financial_exposure=Decimal("5000.00"),
    )
    assert record.score == 12
    assert record.severity == RiskSeverity.HIGH

    # Invalid empty ID
    with pytest.raises(RiskValidationError):
        RiskRecord(
            risk_id="",
            category="Scope",
            description="desc",
            likelihood=3,
            impact=3,
            owner="EM",
            mitigation="action",
        )

    # Invalid negative financial exposure
    with pytest.raises(RiskValidationError):
        RiskRecord(
            risk_id="RSK-002",
            category="Scope",
            description="desc",
            likelihood=3,
            impact=3,
            owner="EM",
            mitigation="action",
            financial_exposure=Decimal("-100.00"),
        )


# 5. Risk prioritization
def test_risk_prioritization():
    """Verify risks are sorted by score descending, then impact, then likelihood."""
    r1 = RiskRecord("R1", "Cat", "Desc", likelihood=2, impact=2, owner="EM", mitigation="Act") # Score 4 (Low)
    r2 = RiskRecord("R2", "Cat", "Desc", likelihood=4, impact=5, owner="EM", mitigation="Act") # Score 20 (Critical)
    r3 = RiskRecord("R3", "Cat", "Desc", likelihood=5, impact=2, owner="EM", mitigation="Act") # Score 10, Impact 2
    r4 = RiskRecord("R4", "Cat", "Desc", likelihood=2, impact=5, owner="EM", mitigation="Act") # Score 10, Impact 5

    sorted_risks = prioritize_risks([r1, r2, r3, r4])
    assert sorted_risks[0].risk_id == "R2"  # Score 20
    assert sorted_risks[1].risk_id == "R4"  # Score 10, Impact 5
    assert sorted_risks[2].risk_id == "R3"  # Score 10, Impact 2
    assert sorted_risks[3].risk_id == "R1"  # Score 4


# 6. Mitigation recommendations for known risk categories
def test_mitigation_plan_generation():
    """Verify actionable mitigation plan is generated from unmitigated risk records."""
    r1 = RiskRecord("R1", "Pricing", "Discount concession", 4, 4, "Commercial Partner", "Escalate for partner review")
    r2 = RiskRecord("R2", "Scope", "Scope creep", 3, 3, "Engagement Manager", "Hold change control workshop")
    r3 = RiskRecord("R3", "Legal", "Contract terms", 1, 1, "Legal Counsel", "MSA review", status="Mitigated")

    plan = generate_mitigation_plan([r1, r2, r3])
    # Mitigated risk should be excluded from active plan
    assert len(plan) == 2
    assert plan[0].risk_id == "R1"
    assert plan[0].suggested_role == "Commercial Partner"
    assert "Critical severity risk" in plan[0].trigger_rationale


# 7. Proposal-readiness score calculation
def test_proposal_readiness_calculation():
    """Verify readiness score computation and denominator handling."""
    checklist = [
        ChecklistItem("C1", "Scope", "Item 1", "desc", ChecklistStatus.COMPLETED),
        ChecklistItem("C2", "Scope", "Item 2", "desc", ChecklistStatus.COMPLETED),
        ChecklistItem("C3", "Scope", "Item 3", "desc", ChecklistStatus.IN_PROGRESS),
        ChecklistItem("C4", "Scope", "Item 4", "desc", ChecklistStatus.NOT_STARTED),
        ChecklistItem("C5", "Legal", "Item 5", "desc", ChecklistStatus.NOT_APPLICABLE),
    ]
    # Total = 5, Applicable = 4 (excluding N/A), Completed = 2 -> 2/4 = 50.0%
    readiness = calculate_proposal_readiness(checklist)
    assert readiness.total_items == 5
    assert readiness.applicable_items == 4
    assert readiness.completed_items == 2
    assert readiness.completion_pct == Decimal("50.00")
    assert readiness.is_ready_for_review is False


# 8. Empty and fully completed checklists
def test_empty_and_fully_completed_checklists():
    """Verify edge cases for empty and 100% completed checklists."""
    empty_res = calculate_proposal_readiness([])
    assert empty_res.total_items == 0
    assert empty_res.completion_pct == Decimal("0.0")

    full_checklist = [
        ChecklistItem("C1", "Scope", "Item 1", "desc", ChecklistStatus.COMPLETED),
        ChecklistItem("C2", "Pricing", "Item 2", "desc", ChecklistStatus.COMPLETED),
    ]
    full_res = calculate_proposal_readiness(full_checklist)
    assert full_res.completion_pct == Decimal("100.00")
    assert full_res.is_ready_for_review is True


# 9. Zero revenue and undefined margin in stress testing
def test_financial_stress_cases_zero_revenue_and_cost():
    """Verify financial stress cases handle zero revenue without division by zero errors."""
    zero_rev_in = CommercialInputs.create(
        base_quoted_price="0.00",
        delivery_costs="40000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    res_zero = calculate_commercials(zero_rev_in)
    stress_cases = evaluate_financial_stress_cases(zero_rev_in, res_zero)

    assert len(stress_cases) == 3
    for sc in stress_cases:
        assert sc.stressed_revenue == Decimal("0.00")
        assert sc.stressed_profit < Decimal("0.00")
        assert sc.stressed_margin_pct is None


# 10. Financial stress cases reconcile with existing commercial engine
def test_financial_stress_cases_reconciliation(baseline_inputs):
    """Verify stressed profits reconcile exactly with existing commercial engine."""
    baseline_res = calculate_commercials(baseline_inputs)
    stress_cases = evaluate_financial_stress_cases(baseline_inputs, baseline_res)

    assert len(stress_cases) == 3
    # Case 1: Delivery labor overrun shock (+20% on 50k delivery = +10k cost)
    c1 = stress_cases[0]
    assert c1.profit_impact == Decimal("-10000.00")
    assert c1.stressed_profit == baseline_res.profit - Decimal("10000.00")
    assert c1.stressed_cost == baseline_res.scenario_total_cost + Decimal("10000.00")

    # Case 2: Discount concession shock (+10% on 100k base = -10k revenue)
    c2 = stress_cases[1]
    assert c2.profit_impact == Decimal("-10000.00")
    assert c2.stressed_revenue == baseline_res.net_revenue - Decimal("10000.00")


# 11. No double-counting of explicitly included costs
def test_no_double_counting_in_stress_cases(baseline_inputs):
    """Verify stress test notes and flags document non-overlapping exposure modeling."""
    baseline_res = calculate_commercials(baseline_inputs)
    stress_cases = evaluate_financial_stress_cases(baseline_inputs, baseline_res)

    for sc in stress_cases:
        assert sc.is_double_counted is False
        assert len(sc.double_counting_note) > 0


# 12. CSV export structure
def test_risk_csv_export_structure(baseline_inputs):
    """Verify exported CSV contains risk register, checklist, and stress cases sections."""
    baseline_res = calculate_commercials(baseline_inputs)
    risks = generate_suggested_risk_flags(baseline_inputs, baseline_res)
    checklist = get_default_readiness_checklist()
    stress_cases = evaluate_financial_stress_cases(baseline_inputs, baseline_res)

    csv_data = export_risk_assessment_csv(risks, checklist, stress_cases, "USD")

    assert "DEALWISE COMMERCIAL RISK INTELLIGENCE & GOVERNANCE REPORT" in csv_data
    assert "SECTION 1: COMMERCIAL RISK REGISTER" in csv_data
    assert "SECTION 2: PROPOSAL READINESS GOVERNANCE CHECKLIST" in csv_data
    assert "SECTION 3: FINANCIAL EXPOSURE STRESS-TEST SCENARIOS" in csv_data

    # Parse with standard csv reader
    import io, csv as std_csv
    rows = list(std_csv.reader(io.StringIO(csv_data)))
    assert len(rows) > 15

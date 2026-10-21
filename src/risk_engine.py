"""Commercial risk intelligence, scoring, readiness checklists, and exposure modeling.

Phase 5: Transparent rule-based risk assessment, ordinal scoring, proposal readiness,
and financial stress-testing using the existing commercial calculation engine.
All monetary calculations preserve Python Decimal precision.
"""

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import enum
import io
import csv
from typing import Any, Dict, List, Optional, Tuple, Union

from src.commercial_engine import (
    CENTS_QUANTIZE,
    PERCENT_QUANTIZE,
    CommercialInputs,
    CommercialResult,
    CommercialValidationError,
    calculate_commercials,
    format_currency,
    format_percentage,
    _to_decimal,
)


class RiskSeverity(str, enum.Enum):
    """Categorical severity levels derived from transparent ordinal score bands."""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


class ChecklistStatus(str, enum.Enum):
    """Status options for proposal readiness governance items."""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    NOT_APPLICABLE = "Not Applicable"


class RiskValidationError(ValueError):
    """Raised when risk record inputs or checklist items fail validation."""
    pass


# Configurable score band definitions: score = likelihood (1-5) * impact (1-5)
# Range: 1 to 25
SCORE_BAND_LOW_MAX = 4         # Scores 1-4
SCORE_BAND_MODERATE_MAX = 9    # Scores 5-9
SCORE_BAND_HIGH_MAX = 14       # Scores 10-14
# Scores 15-25 are Critical


def calculate_risk_score(likelihood: int, impact: int) -> int:
    """Calculate transparent ordinal risk score: Likelihood x Impact.
    
    Likelihood and Impact must be integers from 1 to 5.
    """
    if not isinstance(likelihood, int) or isinstance(likelihood, bool):
        raise RiskValidationError(f"Likelihood must be an integer between 1 and 5; received '{likelihood}'.")
    if not isinstance(impact, int) or isinstance(impact, bool):
        raise RiskValidationError(f"Impact must be an integer between 1 and 5; received '{impact}'.")

    if likelihood < 1 or likelihood > 5:
        raise RiskValidationError(f"Likelihood must be between 1 and 5 inclusive; received {likelihood}.")
    if impact < 1 or impact > 5:
        raise RiskValidationError(f"Impact must be between 1 and 5 inclusive; received {impact}.")

    return likelihood * impact


def get_risk_severity(score: int) -> RiskSeverity:
    """Map ordinal risk score (1-25) to documented severity band."""
    if score < 1 or score > 25:
        raise RiskValidationError(f"Risk score must be between 1 and 25 inclusive; received {score}.")

    if score <= SCORE_BAND_LOW_MAX:
        return RiskSeverity.LOW
    if score <= SCORE_BAND_MODERATE_MAX:
        return RiskSeverity.MODERATE
    if score <= SCORE_BAND_HIGH_MAX:
        return RiskSeverity.HIGH
    return RiskSeverity.CRITICAL


@dataclass
class RiskRecord:
    """Structured commercial risk record for consulting deal governance."""

    risk_id: str
    category: str
    description: str
    likelihood: int
    impact: int
    owner: str
    mitigation: str
    status: str = "Open"
    financial_exposure: Optional[Decimal] = None
    notes: Optional[str] = None
    is_auto_suggested: bool = False

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        """Validate all record attributes."""
        if not self.risk_id or not isinstance(self.risk_id, str) or not self.risk_id.strip():
            raise RiskValidationError("Risk ID must be a non-empty string.")
        if not self.category or not isinstance(self.category, str) or not self.category.strip():
            raise RiskValidationError("Risk category must be a non-empty string.")
        if not self.description or not isinstance(self.description, str) or not self.description.strip():
            raise RiskValidationError("Risk description must be a non-empty string.")
        if not self.owner or not isinstance(self.owner, str) or not self.owner.strip():
            raise RiskValidationError("Risk owner must be a non-empty string.")

        # Validate score bounds
        calculate_risk_score(self.likelihood, self.impact)

        # Validate financial exposure if present
        if self.financial_exposure is not None:
            if not isinstance(self.financial_exposure, Decimal):
                try:
                    self.financial_exposure = _to_decimal(self.financial_exposure, "financial_exposure")
                except Exception as exc:
                    raise RiskValidationError(f"Invalid financial exposure value: {exc}") from exc
            if self.financial_exposure < Decimal("0"):
                raise RiskValidationError(f"Financial exposure cannot be negative: {self.financial_exposure}")

    @property
    def score(self) -> int:
        """Return computed ordinal risk score."""
        return calculate_risk_score(self.likelihood, self.impact)

    @property
    def severity(self) -> RiskSeverity:
        """Return derived severity band."""
        return get_risk_severity(self.score)


def prioritize_risks(risks: List[RiskRecord]) -> List[RiskRecord]:
    """Sort risk records in descending order of priority.
    
    Priority order: Risk Score (desc), Impact (desc), Likelihood (desc), Risk ID (asc).
    """
    return sorted(
        risks,
        key=lambda r: (-r.score, -r.impact, -r.likelihood, r.risk_id),
    )


@dataclass(frozen=True)
class ChecklistItem:
    """Proposal readiness governance item."""

    item_id: str
    category: str
    title: str
    description: str
    status: ChecklistStatus = ChecklistStatus.NOT_STARTED
    notes: Optional[str] = None

    def validate(self) -> None:
        if not self.item_id or not self.item_id.strip():
            raise RiskValidationError("Checklist item ID cannot be empty.")
        if not self.title or not self.title.strip():
            raise RiskValidationError("Checklist item title cannot be empty.")
        if not isinstance(self.status, ChecklistStatus):
            raise RiskValidationError(f"Invalid checklist status: {self.status}")


@dataclass(frozen=True)
class ReadinessResult:
    """Summary metrics of proposal readiness checklist."""

    total_items: int
    applicable_items: int
    completed_items: int
    in_progress_items: int
    not_started_items: int
    completion_pct: Decimal  # In percentage points, e.g. 75.0%
    is_ready_for_review: bool
    summary_narrative: str


def calculate_proposal_readiness(checklist: List[ChecklistItem]) -> ReadinessResult:
    """Calculate governance checklist completion percentage and status.
    
    Denominator excludes Not Applicable items.
    Readiness does NOT mean the proposal is approved.
    """
    if not checklist:
        return ReadinessResult(
            total_items=0,
            applicable_items=0,
            completed_items=0,
            in_progress_items=0,
            not_started_items=0,
            completion_pct=Decimal("0.0"),
            is_ready_for_review=False,
            summary_narrative="No checklist items defined.",
        )

    for item in checklist:
        item.validate()

    total = len(checklist)
    completed = sum(1 for item in checklist if item.status == ChecklistStatus.COMPLETED)
    in_prog = sum(1 for item in checklist if item.status == ChecklistStatus.IN_PROGRESS)
    not_started = sum(1 for item in checklist if item.status == ChecklistStatus.NOT_STARTED)
    not_app = sum(1 for item in checklist if item.status == ChecklistStatus.NOT_APPLICABLE)

    applicable = total - not_app

    if applicable > 0:
        pct = (Decimal(completed) / Decimal(applicable)) * Decimal("100")
        pct = pct.quantize(PERCENT_QUANTIZE, rounding=ROUND_HALF_UP)
    else:
        pct = Decimal("100.0")

    is_ready = pct >= Decimal("80.0") and completed > 0

    if pct == Decimal("100.0"):
        narrative = "All applicable governance checklist items completed. Proposal is ready for final partner review and commercial sign-off."
    elif pct >= Decimal("75.0"):
        narrative = f"Proposal readiness is advanced ({pct}%). Core scoping and commercial checks complete; resolve outstanding items before submission."
    elif pct >= Decimal("50.0"):
        narrative = f"Proposal readiness is in progress ({pct}%). Multiple critical scoping, resourcing, or legal items remain open."
    else:
        narrative = f"Proposal readiness is low ({pct}%). Substantial commercial diligence and contract scoping required prior to executive sign-off."

    return ReadinessResult(
        total_items=total,
        applicable_items=applicable,
        completed_items=completed,
        in_progress_items=in_prog,
        not_started_items=not_started,
        completion_pct=pct,
        is_ready_for_review=is_ready,
        summary_narrative=narrative,
    )


def get_default_readiness_checklist() -> List[ChecklistItem]:
    """Generate standard consulting proposal governance checklist."""
    return [
        ChecklistItem(
            item_id="CHK-01",
            category="Scope & Delivery",
            title="Scope & Deliverables Confirmed",
            description="Clear statement of work, milestone deliverables, and client acceptance criteria documented.",
            status=ChecklistStatus.COMPLETED,
        ),
        ChecklistItem(
            item_id="CHK-02",
            category="Scope & Delivery",
            title="Assumptions & Exclusions Explicit",
            description="Clear project boundaries, client dependencies, and out-of-scope exclusions formally stated.",
            status=ChecklistStatus.COMPLETED,
        ),
        ChecklistItem(
            item_id="CHK-03",
            category="Estimates & Resourcing",
            title="Delivery Effort Estimates Validated",
            description="Workstream duration and role hours reviewed and peer-benchmarked by technical SME.",
            status=ChecklistStatus.IN_PROGRESS,
        ),
        ChecklistItem(
            item_id="CHK-04",
            category="Estimates & Resourcing",
            title="Resource Availability & Pyramid Confirmed",
            description="Named team members or target staffing tiers locked in practice scheduling system.",
            status=ChecklistStatus.IN_PROGRESS,
        ),
        ChecklistItem(
            item_id="CHK-05",
            category="Commercial & Pricing",
            title="Pricing & Discount Approvals Obtained",
            description="Discount rate, blended bill rates, and target gross margin signed off per delegation matrix.",
            status=ChecklistStatus.IN_PROGRESS,
        ),
        ChecklistItem(
            item_id="CHK-06",
            category="Commercial & Pricing",
            title="Payment Terms & Invoicing Schedule Reviewed",
            description="Payment milestone schedule, net payment days, and expenses pass-through terms agreed.",
            status=ChecklistStatus.NOT_STARTED,
        ),
        ChecklistItem(
            item_id="CHK-07",
            category="Legal & Governance",
            title="Client Dependencies & Obligations Documented",
            description="Required client data access, stakeholder interviews, and technical environments specified.",
            status=ChecklistStatus.COMPLETED,
        ),
        ChecklistItem(
            item_id="CHK-08",
            category="Legal & Governance",
            title="Legal & Contractual Review Completed",
            description="Master Services Agreement (MSA), liability caps, and IP terms vetted by commercial counsel.",
            status=ChecklistStatus.NOT_STARTED,
        ),
    ]


@dataclass(frozen=True)
class FinancialStressCase:
    """Stress-test scenario quantifying financial impact of an adverse operational event."""

    name: str
    description: str
    assumptions: str
    baseline_revenue: Decimal
    baseline_cost: Decimal
    baseline_profit: Decimal
    baseline_margin_pct: Optional[Decimal]
    stressed_revenue: Decimal
    stressed_cost: Decimal
    stressed_profit: Decimal
    stressed_margin_pct: Optional[Decimal]
    profit_impact: Decimal        # Stressed profit - Baseline profit (typically negative)
    margin_impact_pp: Optional[Decimal]  # Stressed margin - Baseline margin (percentage points)
    is_double_counted: bool       # Flag indicating whether exposure is already embedded in baseline inputs
    double_counting_note: str


def evaluate_financial_stress_cases(
    inputs: CommercialInputs,
    baseline_result: CommercialResult,
) -> List[FinancialStressCase]:
    """Model deterministic financial stress cases using the existing commercial calculation engine.
    
    Models:
    1. Delivery Labor Overrun Shock (+20% labor overrun)
    2. Client Discount Concession Shock (+10% discount concession)
    3. Compound Adverse Friction (+20% overrun and +10% discount)
    
    Strictly prevents double counting and clearly explains assumptions.
    """
    cases: List[FinancialStressCase] = []

    # Case 1: Labor Cost Overrun Shock (+20% delivery overrun)
    # Check if baseline already has overrun modeled
    baseline_overrun = inputs.cost_overrun_pct
    shock_overrun = baseline_overrun + Decimal("0.20")
    if shock_overrun > Decimal("5.0"):
        shock_overrun = Decimal("5.0")

    in_overrun = CommercialInputs(
        base_quoted_price=inputs.base_quoted_price,
        delivery_costs=inputs.delivery_costs,
        software_tooling_costs=inputs.software_tooling_costs,
        other_expenses=inputs.other_expenses,
        contingency_pct=inputs.contingency_pct,
        discount_pct=inputs.discount_pct,
        cost_overrun_pct=shock_overrun,
        target_margin_pct=inputs.target_margin_pct,
    )
    in_overrun.validate()
    res_overrun = calculate_commercials(in_overrun)

    margin_pp_1 = (
        res_overrun.profit_margin_pct - baseline_result.profit_margin_pct
        if res_overrun.profit_margin_pct is not None and baseline_result.profit_margin_pct is not None
        else None
    )

    cases.append(
        FinancialStressCase(
            name="Delivery Labor Overrun Shock (+20% Scope Creep)",
            description="Simulates unexpected scope elongation or onboarding friction increasing direct labor delivery costs by an additional +20%.",
            assumptions=f"Labor costs increase by 20% on {inputs.delivery_costs}. Quoted price and discounts held constant.",
            baseline_revenue=baseline_result.net_revenue,
            baseline_cost=baseline_result.scenario_total_cost,
            baseline_profit=baseline_result.profit,
            baseline_margin_pct=baseline_result.profit_margin_pct,
            stressed_revenue=res_overrun.net_revenue,
            stressed_cost=res_overrun.scenario_total_cost,
            stressed_profit=res_overrun.profit,
            stressed_margin_pct=res_overrun.profit_margin_pct,
            profit_impact=res_overrun.profit - baseline_result.profit,
            margin_impact_pp=margin_pp_1,
            is_double_counted=False,
            double_counting_note="This shock models unbudgeted labor delivery expansion beyond baseline contingency.",
        )
    )

    # Case 2: Discount Concession Shock (+10% discount)
    baseline_disc = inputs.discount_pct
    shock_disc = baseline_disc + Decimal("0.10")
    if shock_disc > Decimal("1.0"):
        shock_disc = Decimal("1.0")

    in_disc = CommercialInputs(
        base_quoted_price=inputs.base_quoted_price,
        delivery_costs=inputs.delivery_costs,
        software_tooling_costs=inputs.software_tooling_costs,
        other_expenses=inputs.other_expenses,
        contingency_pct=inputs.contingency_pct,
        discount_pct=shock_disc,
        cost_overrun_pct=inputs.cost_overrun_pct,
        target_margin_pct=inputs.target_margin_pct,
    )
    in_disc.validate()
    res_disc = calculate_commercials(in_disc)

    margin_pp_2 = (
        res_disc.profit_margin_pct - baseline_result.profit_margin_pct
        if res_disc.profit_margin_pct is not None and baseline_result.profit_margin_pct is not None
        else None
    )

    cases.append(
        FinancialStressCase(
            name="Commercial Price Concession Shock (+10% Client Discount)",
            description="Simulates aggressive late-stage procurement negotiation forcing an additional 10% discount concession.",
            assumptions=f"Client discount increases from {inputs.discount_pct * Decimal('100')}% to {shock_disc * Decimal('100')}%. Costs remain fixed.",
            baseline_revenue=baseline_result.net_revenue,
            baseline_cost=baseline_result.scenario_total_cost,
            baseline_profit=baseline_result.profit,
            baseline_margin_pct=baseline_result.profit_margin_pct,
            stressed_revenue=res_disc.net_revenue,
            stressed_cost=res_disc.scenario_total_cost,
            stressed_profit=res_disc.profit,
            stressed_margin_pct=res_disc.profit_margin_pct,
            profit_impact=res_disc.profit - baseline_result.profit,
            margin_impact_pp=margin_pp_2,
            is_double_counted=False,
            double_counting_note="Models fee concession impact without altering delivery expenditure.",
        )
    )

    # Case 3: Compound Downside Friction (+20% overrun & +10% discount)
    in_compound = CommercialInputs(
        base_quoted_price=inputs.base_quoted_price,
        delivery_costs=inputs.delivery_costs,
        software_tooling_costs=inputs.software_tooling_costs,
        other_expenses=inputs.other_expenses,
        contingency_pct=inputs.contingency_pct,
        discount_pct=shock_disc,
        cost_overrun_pct=shock_overrun,
        target_margin_pct=inputs.target_margin_pct,
    )
    in_compound.validate()
    res_compound = calculate_commercials(in_compound)

    margin_pp_3 = (
        res_compound.profit_margin_pct - baseline_result.profit_margin_pct
        if res_compound.profit_margin_pct is not None and baseline_result.profit_margin_pct is not None
        else None
    )

    cases.append(
        FinancialStressCase(
            name="Compound Downside Friction (Labor Overrun + Price Concession)",
            description="Simultaneous occurrence of adverse pricing concessions and delivery execution delays.",
            assumptions=f"Discount at {shock_disc * Decimal('100')}% and labor overrun at {shock_overrun * Decimal('100')}%.",
            baseline_revenue=baseline_result.net_revenue,
            baseline_cost=baseline_result.scenario_total_cost,
            baseline_profit=baseline_result.profit,
            baseline_margin_pct=baseline_result.profit_margin_pct,
            stressed_revenue=res_compound.net_revenue,
            stressed_cost=res_compound.scenario_total_cost,
            stressed_profit=res_compound.profit,
            stressed_margin_pct=res_compound.profit_margin_pct,
            profit_impact=res_compound.profit - baseline_result.profit,
            margin_impact_pp=margin_pp_3,
            is_double_counted=False,
            double_counting_note="Evaluates combined pressure on operating profit and margin viability.",
        )
    )

    return cases


def generate_suggested_risk_flags(
    inputs: CommercialInputs,
    result: CommercialResult,
) -> List[RiskRecord]:
    """Generate transparent rule-based risk flags based on current commercial inputs."""
    suggested: List[RiskRecord] = []

    # 1. Discount Risk: discount >= 10%
    if inputs.discount_pct >= Decimal("0.10"):
        suggested.append(
            RiskRecord(
                risk_id="RSK-DISC",
                category="Commercial & Pricing",
                description=f"Client discount concession is high ({format_percentage(inputs.discount_pct * Decimal('100'))}), significantly reducing net revenue.",
                likelihood=4,
                impact=4,
                owner="Commercial Partner",
                mitigation="Request executive commercial approval and negotiate phased scope concessions in exchange for discount.",
                status="Open",
                financial_exposure=inputs.base_quoted_price * inputs.discount_pct,
                notes="Rule-based flag: discount exceeds 10% benchmark.",
                is_auto_suggested=True,
            )
        )

    # 2. Margin Deficit Risk: actual margin < target margin
    if result.profit_margin_pct is not None and not result.meets_target_margin:
        suggested.append(
            RiskRecord(
                risk_id="RSK-MARG",
                category="Commercial & Pricing",
                description=f"Projected margin ({format_percentage(result.profit_margin_pct)}) is below practice target ({format_percentage(inputs.target_margin_pct * Decimal('100'))}).",
                likelihood=4,
                impact=5,
                owner="Pricing Director",
                mitigation=f"Recalibrate staffing leverage or quote at least {result.required_quoted_price} before discount to restore target margin.",
                status="Open",
                financial_exposure=abs(result.profit),
                notes="Rule-based flag: projected margin fails practice threshold.",
                is_auto_suggested=True,
            )
        )

    # 3. Operating Loss Risk: profit < 0
    if result.profit < Decimal("0"):
        suggested.append(
            RiskRecord(
                risk_id="RSK-LOSS",
                category="Commercial & Pricing",
                description=f"Engagement operates at an estimated net deficit of {result.profit}.",
                likelihood=5,
                impact=5,
                owner="Practice Lead",
                mitigation="Halt proposal submission until pricing or delivery scope is restructured to exceed break-even revenue.",
                status="Open",
                financial_exposure=abs(result.profit),
                notes="Rule-based flag: engagement is loss-making.",
                is_auto_suggested=True,
            )
        )

    # 4. Low Contingency Buffer: contingency < 10%
    if inputs.contingency_pct < Decimal("0.10"):
        suggested.append(
            RiskRecord(
                risk_id="RSK-CONT",
                category="Scope & Delivery",
                description=f"Contingency buffer is lean ({format_percentage(inputs.contingency_pct * Decimal('100'))}) for advisory engagement complexity.",
                likelihood=3,
                impact=3,
                owner="Engagement Manager",
                mitigation="Increase contingency reserve to at least 10% on direct estimated costs to absorb unplanned rework.",
                status="Open",
                financial_exposure=result.direct_estimated_cost * Decimal("0.05"),
                notes="Rule-based flag: contingency reserve below 10% standard practice buffer.",
                is_auto_suggested=True,
            )
        )

    # Standard baseline advisory risks if list is small
    if len(suggested) < 3:
        suggested.append(
            RiskRecord(
                risk_id="RSK-SCOPE",
                category="Scope & Delivery",
                description="Technical delivery scope has unconfirmed client data ingestion assumptions.",
                likelihood=3,
                impact=3,
                owner="Solutions Architect",
                mitigation="Conduct technical discovery sprint and explicitly define data readiness prerequisites in proposal.",
                status="Open",
                financial_exposure=inputs.delivery_costs * Decimal("0.10"),
                notes="Standard demonstration risk archetype.",
                is_auto_suggested=True,
            )
        )
        suggested.append(
            RiskRecord(
                risk_id="RSK-STAFF",
                category="Staffing & Resourcing",
                description="Senior technical specialist bandwidth has not been formally allocated.",
                likelihood=2,
                impact=4,
                owner="Staffing Manager",
                mitigation="Pre-reserve named key personnel in resource scheduling system prior to contract sign-off.",
                status="In Progress",
                financial_exposure=None,
                notes="Standard demonstration risk archetype.",
                is_auto_suggested=True,
            )
        )

    return suggested


@dataclass(frozen=True)
class MitigationAction:
    """Actionable recommendation mapped to detected commercial risks."""

    priority_rank: int
    risk_id: str
    category: str
    suggested_role: str
    action_text: str
    trigger_rationale: str


def generate_mitigation_plan(risks: List[RiskRecord]) -> List[MitigationAction]:
    """Generate prioritized mitigation actions from risk records."""
    sorted_risks = prioritize_risks(risks)
    plan: List[MitigationAction] = []

    for idx, r in enumerate(sorted_risks, start=1):
        if r.status.lower() in ("mitigated", "closed"):
            continue

        trigger = f"{r.severity.value} severity risk (Score: {r.score}/25) in {r.category}."
        plan.append(
            MitigationAction(
                priority_rank=idx,
                risk_id=r.risk_id,
                category=r.category,
                suggested_role=r.owner,
                action_text=r.mitigation,
                trigger_rationale=trigger,
            )
        )

    return plan


def export_risk_assessment_csv(
    risks: List[RiskRecord],
    checklist: List[ChecklistItem],
    stress_cases: List[FinancialStressCase],
    currency: str = "USD",
) -> str:
    """Generate comprehensive CSV export of risk register, checklist, and financial exposure stress cases."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["DEALWISE COMMERCIAL RISK INTELLIGENCE & GOVERNANCE REPORT"])
    writer.writerow(["Display Currency", currency])
    writer.writerow(["Methodology", "Ordinal Risk Scoring (L x I) & Deterministic Financial Stress Testing"])
    writer.writerow([])

    # Section 1: Risk Register
    writer.writerow(["SECTION 1: COMMERCIAL RISK REGISTER"])
    writer.writerow([
        "Risk ID",
        "Category",
        "Description",
        "Likelihood (1-5)",
        "Impact (1-5)",
        "Risk Score (1-25)",
        "Severity",
        "Owner",
        "Mitigation Action",
        "Status",
        f"Financial Exposure ({currency})",
        "Auto-Suggested",
        "Notes",
    ])
    for r in prioritize_risks(risks):
        exp_str = f"{r.financial_exposure:.2f}" if r.financial_exposure is not None else "N/A"
        writer.writerow([
            r.risk_id,
            r.category,
            r.description,
            r.likelihood,
            r.impact,
            r.score,
            r.severity.value,
            r.owner,
            r.mitigation,
            r.status,
            exp_str,
            "YES" if r.is_auto_suggested else "NO",
            r.notes or "",
        ])
    writer.writerow([])

    # Section 2: Proposal Readiness Checklist
    writer.writerow(["SECTION 2: PROPOSAL READINESS GOVERNANCE CHECKLIST"])
    writer.writerow(["Item ID", "Category", "Title", "Description", "Status", "Notes"])
    for item in checklist:
        writer.writerow([
            item.item_id,
            item.category,
            item.title,
            item.description,
            item.status.value,
            item.notes or "",
        ])
    writer.writerow([])

    # Section 3: Financial Exposure Stress Cases
    writer.writerow(["SECTION 3: FINANCIAL EXPOSURE STRESS-TEST SCENARIOS"])
    writer.writerow([
        "Stress Case Name",
        "Assumptions",
        f"Baseline Revenue ({currency})",
        f"Baseline Cost ({currency})",
        f"Baseline Profit ({currency})",
        "Baseline Margin (%)",
        f"Stressed Revenue ({currency})",
        f"Stressed Cost ({currency})",
        f"Stressed Profit ({currency})",
        "Stressed Margin (%)",
        f"Profit Impact ({currency})",
        "Margin Impact (pp)",
        "Double-Counting Transparency Note",
    ])
    for sc in stress_cases:
        base_m = f"{sc.baseline_margin_pct:.2f}" if sc.baseline_margin_pct is not None else "N/A"
        stress_m = f"{sc.stressed_margin_pct:.2f}" if sc.stressed_margin_pct is not None else "N/A"
        m_impact = f"{sc.margin_impact_pp:.2f}" if sc.margin_impact_pp is not None else "N/A"
        writer.writerow([
            sc.name,
            sc.assumptions,
            f"{sc.baseline_revenue:.2f}",
            f"{sc.baseline_cost:.2f}",
            f"{sc.baseline_profit:.2f}",
            base_m,
            f"{sc.stressed_revenue:.2f}",
            f"{sc.stressed_cost:.2f}",
            f"{sc.stressed_profit:.2f}",
            stress_m,
            f"{sc.profit_impact:.2f}",
            m_impact,
            sc.double_counting_note,
        ])

    return output.getvalue()

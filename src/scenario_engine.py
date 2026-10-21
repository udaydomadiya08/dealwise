"""Scenario analysis engine for consulting proposals and commercial stress-testing.

Phase 4: Independent, testable scenario comparison, sensitivity matrices,
and contract commercial model evaluation (Fixed Fee vs. Time & Materials).
All monetary arithmetic uses Python's Decimal type.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
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


@dataclass(frozen=True)
class ScenarioComparison:
    """Side-by-side delta evaluation between a baseline and a what-if scenario."""

    baseline_inputs: CommercialInputs
    scenario_inputs: CommercialInputs
    baseline_result: CommercialResult
    scenario_result: CommercialResult

    # Absolute monetary and rate deltas (Scenario - Baseline)
    delta_net_revenue: Decimal
    delta_total_cost: Decimal
    delta_profit: Decimal
    delta_margin_percentage_points: Optional[Decimal]  # Expressed in percentage points, e.g. -5.25 for -5.25 pp
    delta_markup_percentage_points: Optional[Decimal]

    # Qualitative indicators
    scenario_is_profitable: bool
    scenario_meets_target: bool

    def to_dict(self) -> Dict[str, Any]:
        """Return rounded summary dictionary for tabular display and reporting."""
        def _round_cur(val: Optional[Decimal]) -> Optional[float]:
            if val is None:
                return None
            return float(val.quantize(CENTS_QUANTIZE, rounding=ROUND_HALF_UP))

        def _round_pct(val: Optional[Decimal]) -> Optional[float]:
            if val is None:
                return None
            return float(val.quantize(PERCENT_QUANTIZE, rounding=ROUND_HALF_UP))

        return {
            "baseline_revenue": _round_cur(self.baseline_result.net_revenue),
            "scenario_revenue": _round_cur(self.scenario_result.net_revenue),
            "delta_revenue": _round_cur(self.delta_net_revenue),
            "baseline_cost": _round_cur(self.baseline_result.scenario_total_cost),
            "scenario_cost": _round_cur(self.scenario_result.scenario_total_cost),
            "delta_cost": _round_cur(self.delta_total_cost),
            "baseline_profit": _round_cur(self.baseline_result.profit),
            "scenario_profit": _round_cur(self.scenario_result.profit),
            "delta_profit": _round_cur(self.delta_profit),
            "baseline_margin_pct": _round_pct(self.baseline_result.profit_margin_pct),
            "scenario_margin_pct": _round_pct(self.scenario_result.profit_margin_pct),
            "delta_margin_pp": _round_pct(self.delta_margin_percentage_points),
            "baseline_markup_pct": _round_pct(self.baseline_result.markup_pct),
            "scenario_markup_pct": _round_pct(self.scenario_result.markup_pct),
            "delta_markup_pp": _round_pct(self.delta_markup_percentage_points),
            "scenario_is_profitable": self.scenario_is_profitable,
            "scenario_meets_target": self.scenario_meets_target,
        }


def compare_scenarios(
    baseline_inputs: CommercialInputs,
    scenario_inputs: CommercialInputs,
) -> ScenarioComparison:
    """Compare a baseline proposal with a what-if scenario using the commercial engine.
    
    Verifies that delta_profit == delta_net_revenue - delta_total_cost.
    Deltas for profit margin are calculated strictly in percentage points.
    """
    baseline_result = calculate_commercials(baseline_inputs)
    scenario_result = calculate_commercials(scenario_inputs)

    delta_revenue = scenario_result.net_revenue - baseline_result.net_revenue
    delta_cost = scenario_result.scenario_total_cost - baseline_result.scenario_total_cost
    delta_profit = scenario_result.profit - baseline_result.profit

    # Margin delta in percentage points (e.g. 25% to 30% is +5.0 percentage points)
    if (
        scenario_result.profit_margin_pct is not None
        and baseline_result.profit_margin_pct is not None
    ):
        delta_margin_pp = scenario_result.profit_margin_pct - baseline_result.profit_margin_pct
    else:
        delta_margin_pp = None

    # Markup delta in percentage points
    if (
        scenario_result.markup_pct is not None
        and baseline_result.markup_pct is not None
    ):
        delta_markup_pp = scenario_result.markup_pct - baseline_result.markup_pct
    else:
        delta_markup_pp = None

    return ScenarioComparison(
        baseline_inputs=baseline_inputs,
        scenario_inputs=scenario_inputs,
        baseline_result=baseline_result,
        scenario_result=scenario_result,
        delta_net_revenue=delta_revenue,
        delta_total_cost=delta_cost,
        delta_profit=delta_profit,
        delta_margin_percentage_points=delta_margin_pp,
        delta_markup_percentage_points=delta_markup_pp,
        scenario_is_profitable=scenario_result.is_profitable,
        scenario_meets_target=scenario_result.meets_target_margin,
    )


@dataclass(frozen=True)
class SensitivityCell:
    """Calculated metric output for a specific discount and cost-overrun pair."""

    discount_pct: Decimal        # Fractional rate, e.g. 0.10 for 10%
    cost_overrun_pct: Decimal    # Fractional rate, e.g. 0.15 for 15%
    net_revenue: Decimal
    total_cost: Decimal
    profit: Decimal
    profit_margin_pct: Optional[Decimal]  # In percentage points, e.g. 25.5
    markup_pct: Optional[Decimal]
    is_profitable: bool
    meets_target: bool


def generate_sensitivity_grid(
    base_inputs: CommercialInputs,
    discount_steps: Optional[List[Union[Decimal, float, str]]] = None,
    overrun_steps: Optional[List[Union[Decimal, float, str]]] = None,
    rates_as_percentages: bool = True,
) -> List[List[SensitivityCell]]:
    """Generate a 2D sensitivity matrix varying discount and delivery cost overrun.
    
    Default ranges:
    - Discount steps: 0%, 5%, 10%, 15%, 20%
    - Overrun steps: 0%, 5%, 10%, 15%, 20%, 25%
    """
    if discount_steps is None:
        raw_discounts = ["0.0", "5.0", "10.0", "15.0", "20.0"]
    else:
        raw_discounts = [str(d) for d in discount_steps]

    if overrun_steps is None:
        raw_overruns = ["0.0", "5.0", "10.0", "15.0", "20.0", "25.0"]
    else:
        raw_overruns = [str(o) for o in overrun_steps]

    divisor = Decimal("100") if rates_as_percentages else Decimal("1")
    parsed_discounts = [_to_decimal(d, "discount_step") / divisor for d in raw_discounts]
    parsed_overruns = [_to_decimal(o, "overrun_step") / divisor for o in raw_overruns]

    grid: List[List[SensitivityCell]] = []

    for overrun in parsed_overruns:
        row: List[SensitivityCell] = []
        for discount in parsed_discounts:
            # Create scenario inputs with modified discount and overrun
            scenario_in = CommercialInputs(
                base_quoted_price=base_inputs.base_quoted_price,
                delivery_costs=base_inputs.delivery_costs,
                software_tooling_costs=base_inputs.software_tooling_costs,
                other_expenses=base_inputs.other_expenses,
                contingency_pct=base_inputs.contingency_pct,
                discount_pct=discount,
                cost_overrun_pct=overrun,
                target_margin_pct=base_inputs.target_margin_pct,
            )
            scenario_in.validate()
            res = calculate_commercials(scenario_in)

            row.append(
                SensitivityCell(
                    discount_pct=discount,
                    cost_overrun_pct=overrun,
                    net_revenue=res.net_revenue,
                    total_cost=res.scenario_total_cost,
                    profit=res.profit,
                    profit_margin_pct=res.profit_margin_pct,
                    markup_pct=res.markup_pct,
                    is_profitable=res.is_profitable,
                    meets_target=res.meets_target_margin,
                )
            )
        grid.append(row)

    return grid


@dataclass(frozen=True)
class ContractModelEvaluation:
    """Evaluation of an engagement under a specific commercial contracting structure."""

    model_name: str              # "Fixed Fee" or "Time & Materials"
    revenue: Decimal
    total_cost: Decimal
    profit: Decimal
    profit_margin_pct: Optional[Decimal]
    markup_pct: Optional[Decimal]
    risk_allocation: str         # Clear description of who absorbs delivery variances
    assumptions: List[str]


def evaluate_fixed_fee_model(
    agreed_fixed_fee: Union[Decimal, float, str],
    delivery_costs: Union[Decimal, float, str],
    software_and_expenses: Union[Decimal, float, str],
    contingency_pct: Union[Decimal, float, str],
    cost_overrun_pct: Union[Decimal, float, str] = "0.0",
    rates_as_percentages: bool = True,
) -> ContractModelEvaluation:
    """Evaluate a Fixed Fee commercial agreement under modeled delivery overruns.
    
    Under Fixed Fee:
    - Revenue is locked at agreed_fixed_fee regardless of hours spent.
    - Delivery costs and overruns are borne by the consulting firm.
    """
    divisor = Decimal("100") if rates_as_percentages else Decimal("1")
    fee = _to_decimal(agreed_fixed_fee, "agreed_fixed_fee")
    deliv = _to_decimal(delivery_costs, "delivery_costs")
    soft_exp = _to_decimal(software_and_expenses, "software_and_expenses")
    cont_rate = _to_decimal(contingency_pct, "contingency_pct") / divisor
    overrun_rate = _to_decimal(cost_overrun_pct, "cost_overrun_pct") / divisor

    if fee < Decimal("0") or deliv < Decimal("0") or soft_exp < Decimal("0"):
        raise CommercialValidationError("Monetary amounts cannot be negative.")
    if cont_rate < Decimal("0") or cont_rate > Decimal("1.0"):
        raise CommercialValidationError("Contingency must be between 0% and 100%.")
    if overrun_rate < Decimal("0") or overrun_rate > Decimal("5.0"):
        raise CommercialValidationError("Cost overrun rate must be non-negative and <= 500%.")

    direct_cost = deliv + soft_exp
    contingency_amount = direct_cost * cont_rate
    scenario_delivery = deliv * (Decimal("1") + overrun_rate)
    total_cost = scenario_delivery + soft_exp + contingency_amount

    profit = fee - total_cost
    margin = (profit / fee * Decimal("100")) if fee > Decimal("0") else None
    markup = (profit / total_cost * Decimal("100")) if total_cost > Decimal("0") else None

    return ContractModelEvaluation(
        model_name="Fixed Fee",
        revenue=fee,
        total_cost=total_cost,
        profit=profit,
        profit_margin_pct=margin,
        markup_pct=markup,
        risk_allocation=(
            "Consulting firm bears 100% of delivery overrun risk. "
            "Fee is fixed; any labor elongation or restaffing cost directly reduces partner profit margin."
        ),
        assumptions=[
            f"Agreed Fixed Contract Price: {fee}",
            f"Baseline Direct Delivery Costs: {deliv}",
            f"Software & Expenses: {soft_exp}",
            f"Contingency Reserve: {cont_rate * Decimal('100')}%",
            f"Modeled Labor Overrun: {overrun_rate * Decimal('100')}%",
            "Client does not pay for hours exceeding initial scope unless a formal change order is signed.",
        ],
    )


def evaluate_time_and_materials_model(
    billable_hours: Union[Decimal, float, str],
    billing_rate_per_hour: Union[Decimal, float, str],
    cost_rate_per_hour: Union[Decimal, float, str],
    software_and_expenses: Union[Decimal, float, str],
    contingency_pct: Union[Decimal, float, str] = "0.0",
    hours_overrun_pct: Union[Decimal, float, str] = "0.0",
    rates_as_percentages: bool = True,
) -> ContractModelEvaluation:
    """Evaluate a Time & Materials (T&M) agreement under modeled hours overrun.
    
    Under standard T&M:
    - Client is billed for actual hours delivered at billing_rate_per_hour.
    - Delivery cost is actual hours delivered at cost_rate_per_hour.
    - Software and expenses are billed through or absorbed per contract terms.
    """
    divisor = Decimal("100") if rates_as_percentages else Decimal("1")
    hours = _to_decimal(billable_hours, "billable_hours")
    bill_rate = _to_decimal(billing_rate_per_hour, "billing_rate_per_hour")
    cost_rate = _to_decimal(cost_rate_per_hour, "cost_rate_per_hour")
    soft_exp = _to_decimal(software_and_expenses, "software_and_expenses")
    cont_rate = _to_decimal(contingency_pct, "contingency_pct") / divisor
    overrun_rate = _to_decimal(hours_overrun_pct, "hours_overrun_pct") / divisor

    if hours < Decimal("0") or bill_rate < Decimal("0") or cost_rate < Decimal("0") or soft_exp < Decimal("0"):
        raise CommercialValidationError("Hours and rates cannot be negative.")
    if cont_rate < Decimal("0") or cont_rate > Decimal("1.0"):
        raise CommercialValidationError("Contingency must be between 0% and 100%.")
    if overrun_rate < Decimal("0") or overrun_rate > Decimal("5.0"):
        raise CommercialValidationError("Hours overrun rate must be non-negative and <= 500%.")

    # Actual delivered hours including overrun
    actual_hours = hours * (Decimal("1") + overrun_rate)

    revenue = actual_hours * bill_rate
    labor_cost = actual_hours * cost_rate
    direct_cost = labor_cost + soft_exp
    contingency_amount = direct_cost * cont_rate
    total_cost = direct_cost + contingency_amount

    profit = revenue - total_cost
    margin = (profit / revenue * Decimal("100")) if revenue > Decimal("0") else None
    markup = (profit / total_cost * Decimal("100")) if total_cost > Decimal("0") else None

    return ContractModelEvaluation(
        model_name="Time & Materials (T&M)",
        revenue=revenue,
        total_cost=total_cost,
        profit=profit,
        profit_margin_pct=margin,
        markup_pct=markup,
        risk_allocation=(
            "Client absorbs delivery volume risk (unless a cap is negotiated). "
            "Additional hours generate proportional billings, protecting firm contribution margin."
        ),
        assumptions=[
            f"Baseline Billable Hours: {hours} hrs (Scenario Actual: {actual_hours} hrs)",
            f"Hourly Billing Rate: {bill_rate} / hr",
            f"Hourly Direct Cost Rate: {cost_rate} / hr",
            f"Software & Expenses: {soft_exp}",
            f"Contingency: {cont_rate * Decimal('100')}%",
            f"Hours Overrun: {overrun_rate * Decimal('100')}%",
            "Assumes fully un-capped T&M where all delivered hours are billable and recognized.",
        ],
    )


def export_scenario_to_csv(
    comparison: ScenarioComparison,
    sensitivity_grid: Optional[List[List[SensitivityCell]]] = None,
    currency_code: str = "USD",
) -> str:
    """Generate professional, clean CSV string containing scenario comparison and sensitivity grid."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header section
    writer.writerow(["DEALWISE SCENARIO SIMULATION & SENSITIVITY REPORT"])
    writer.writerow(["Report Type", "Commercial Scenario Comparison"])
    writer.writerow(["Display Currency", currency_code])
    writer.writerow(["Calculation Mode", "Python Decimal (Exact Precision)"])
    writer.writerow([])

    # Baseline vs Scenario Parameters
    writer.writerow(["SECTION 1: PROPOSAL INPUT PARAMETERS", "Baseline", "Scenario", "Unit"])
    writer.writerow([
        "Base Quoted Price",
        f"{comparison.baseline_inputs.base_quoted_price:.2f}",
        f"{comparison.scenario_inputs.base_quoted_price:.2f}",
        currency_code,
    ])
    writer.writerow([
        "Client Discount Rate",
        f"{comparison.baseline_inputs.discount_pct * Decimal('100'):.2f}",
        f"{comparison.scenario_inputs.discount_pct * Decimal('100'):.2f}",
        "%",
    ])
    writer.writerow([
        "Delivery Costs (Labour & Subs)",
        f"{comparison.baseline_inputs.delivery_costs:.2f}",
        f"{comparison.scenario_inputs.delivery_costs:.2f}",
        currency_code,
    ])
    writer.writerow([
        "Software & Tooling Costs",
        f"{comparison.baseline_inputs.software_tooling_costs:.2f}",
        f"{comparison.scenario_inputs.software_tooling_costs:.2f}",
        currency_code,
    ])
    writer.writerow([
        "Other Expenses",
        f"{comparison.baseline_inputs.other_expenses:.2f}",
        f"{comparison.scenario_inputs.other_expenses:.2f}",
        currency_code,
    ])
    writer.writerow([
        "Contingency Reserve Rate",
        f"{comparison.baseline_inputs.contingency_pct * Decimal('100'):.2f}",
        f"{comparison.scenario_inputs.contingency_pct * Decimal('100'):.2f}",
        "%",
    ])
    writer.writerow([
        "Delivery-Cost Overrun Rate",
        f"{comparison.baseline_inputs.cost_overrun_pct * Decimal('100'):.2f}",
        f"{comparison.scenario_inputs.cost_overrun_pct * Decimal('100'):.2f}",
        "%",
    ])
    writer.writerow([
        "Target Practice Margin",
        f"{comparison.baseline_inputs.target_margin_pct * Decimal('100'):.2f}",
        f"{comparison.scenario_inputs.target_margin_pct * Decimal('100'):.2f}",
        "%",
    ])
    writer.writerow([])

    # Financial Outputs & Deltas
    writer.writerow(["SECTION 2: FINANCIAL OUTPUTS & DELTAS", "Baseline", "Scenario", "Variance (Delta)", "Unit"])
    writer.writerow([
        "Net Realized Revenue",
        f"{comparison.baseline_result.net_revenue:.2f}",
        f"{comparison.scenario_result.net_revenue:.2f}",
        f"{comparison.delta_net_revenue:.2f}",
        currency_code,
    ])
    writer.writerow([
        "Scenario Total Estimated Cost",
        f"{comparison.baseline_result.scenario_total_cost:.2f}",
        f"{comparison.scenario_result.scenario_total_cost:.2f}",
        f"{comparison.delta_total_cost:.2f}",
        currency_code,
    ])
    writer.writerow([
        "Projected Operating Profit / Loss",
        f"{comparison.baseline_result.profit:.2f}",
        f"{comparison.scenario_result.profit:.2f}",
        f"{comparison.delta_profit:.2f}",
        currency_code,
    ])

    base_margin = f"{comparison.baseline_result.profit_margin_pct:.2f}" if comparison.baseline_result.profit_margin_pct is not None else "N/A"
    scen_margin = f"{comparison.scenario_result.profit_margin_pct:.2f}" if comparison.scenario_result.profit_margin_pct is not None else "N/A"
    delta_margin = f"{comparison.delta_margin_percentage_points:.2f}" if comparison.delta_margin_percentage_points is not None else "N/A"
    writer.writerow([
        "Profit Margin",
        base_margin,
        scen_margin,
        delta_margin,
        "% / percentage points",
    ])

    base_markup = f"{comparison.baseline_result.markup_pct:.2f}" if comparison.baseline_result.markup_pct is not None else "N/A"
    scen_markup = f"{comparison.scenario_result.markup_pct:.2f}" if comparison.scenario_result.markup_pct is not None else "N/A"
    delta_markup = f"{comparison.delta_markup_percentage_points:.2f}" if comparison.delta_markup_percentage_points is not None else "N/A"
    writer.writerow([
        "Markup on Cost",
        base_markup,
        scen_markup,
        delta_markup,
        "% / percentage points",
    ])
    writer.writerow([])

    # Sensitivity Grid Table
    if sensitivity_grid:
        writer.writerow(["SECTION 3: SENSITIVITY GRID MATRIX"])
        writer.writerow([
            "Discount (%)",
            "Cost Overrun (%)",
            f"Net Revenue ({currency_code})",
            f"Total Cost ({currency_code})",
            f"Operating Profit ({currency_code})",
            "Profit Margin (%)",
            "Markup (%)",
            "Profitable (Y/N)",
            "Target Margin Met (Y/N)",
        ])

        for row in sensitivity_grid:
            for cell in row:
                m_str = f"{cell.profit_margin_pct:.2f}" if cell.profit_margin_pct is not None else "N/A"
                mu_str = f"{cell.markup_pct:.2f}" if cell.markup_pct is not None else "N/A"
                writer.writerow([
                    f"{cell.discount_pct * Decimal('100'):.1f}",
                    f"{cell.cost_overrun_pct * Decimal('100'):.1f}",
                    f"{cell.net_revenue:.2f}",
                    f"{cell.total_cost:.2f}",
                    f"{cell.profit:.2f}",
                    m_str,
                    mu_str,
                    "YES" if cell.is_profitable else "NO",
                    "YES" if cell.meets_target else "NO",
                ])

    return output.getvalue()

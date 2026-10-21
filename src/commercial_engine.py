"""Commercial calculation engine for consulting proposals and advisory deals.

Phase 2: Independent, tested, high-precision financial calculation engine.
All calculations use Python's Decimal type to avoid binary floating-point inaccuracy.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import math
from typing import Any, Dict, Optional, Union

# Standard financial precision constants
CENTS_QUANTIZE = Decimal("0.01")
PERCENT_QUANTIZE = Decimal("0.01")


class CommercialValidationError(ValueError):
    """Raised when commercial inputs fail domain validation rules."""
    pass


def _to_decimal(val: Any, field_name: str) -> Decimal:
    """Safely convert input value to Decimal, rejecting non-finite and invalid types."""
    if val is None:
        raise CommercialValidationError(f"Field '{field_name}' cannot be None.")

    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            raise CommercialValidationError(
                f"Field '{field_name}' must be a finite number; received non-finite float '{val}'."
            )
        # Convert float via string representation to preserve input precision
        return Decimal(str(val))

    if isinstance(val, (int, str)):
        try:
            d = Decimal(str(val))
            if d.is_nan() or d.is_infinite():
                raise CommercialValidationError(
                    f"Field '{field_name}' must be a finite number."
                )
            return d
        except InvalidOperation as exc:
            raise CommercialValidationError(
                f"Field '{field_name}' cannot be converted to Decimal: {val}"
            ) from exc

    if isinstance(val, Decimal):
        if val.is_nan() or val.is_infinite():
            raise CommercialValidationError(
                f"Field '{field_name}' must be finite Decimal; received '{val}'."
            )
        return val

    raise CommercialValidationError(
        f"Field '{field_name}' has unsupported type '{type(val).__name__}'."
    )


@dataclass(frozen=True)
class CommercialInputs:
    """Normalized commercial inputs for deal modeling.
    
    All percentage inputs are fractional rates (e.g. 0.10 for 10%, 0.25 for 25%).
    Use `from_percentages()` if passing percentage values (e.g. 10.0 for 10%).
    """

    base_quoted_price: Decimal
    delivery_costs: Decimal
    software_tooling_costs: Decimal
    other_expenses: Decimal
    contingency_pct: Decimal  # e.g., Decimal("0.10") for 10%
    discount_pct: Decimal     # e.g., Decimal("0.05") for 5%
    cost_overrun_pct: Decimal # e.g., Decimal("0.15") for 15%
    target_margin_pct: Decimal # e.g., Decimal("0.25") for 25%

    @classmethod
    def create(
        cls,
        base_quoted_price: Union[Decimal, float, int, str],
        delivery_costs: Union[Decimal, float, int, str],
        software_tooling_costs: Union[Decimal, float, int, str],
        other_expenses: Union[Decimal, float, int, str],
        contingency_pct: Union[Decimal, float, int, str],
        discount_pct: Union[Decimal, float, int, str],
        cost_overrun_pct: Union[Decimal, float, int, str],
        target_margin_pct: Union[Decimal, float, int, str],
        rates_as_percentages: bool = False,
    ) -> "CommercialInputs":
        """Factory constructor that converts inputs to Decimal and validates them.
        
        If `rates_as_percentages` is True, inputs like `10.0` for contingency are divided by 100.
        """
        divisor = Decimal("100") if rates_as_percentages else Decimal("1")

        obj = cls(
            base_quoted_price=_to_decimal(base_quoted_price, "base_quoted_price"),
            delivery_costs=_to_decimal(delivery_costs, "delivery_costs"),
            software_tooling_costs=_to_decimal(software_tooling_costs, "software_tooling_costs"),
            other_expenses=_to_decimal(other_expenses, "other_expenses"),
            contingency_pct=_to_decimal(contingency_pct, "contingency_pct") / divisor,
            discount_pct=_to_decimal(discount_pct, "discount_pct") / divisor,
            cost_overrun_pct=_to_decimal(cost_overrun_pct, "cost_overrun_pct") / divisor,
            target_margin_pct=_to_decimal(target_margin_pct, "target_margin_pct") / divisor,
        )
        obj.validate()
        return obj

    @classmethod
    def from_percentages(
        cls,
        base_quoted_price: Union[Decimal, float, int, str],
        delivery_costs: Union[Decimal, float, int, str],
        software_tooling_costs: Union[Decimal, float, int, str],
        other_expenses: Union[Decimal, float, int, str],
        contingency_pct: Union[Decimal, float, int, str],
        discount_pct: Union[Decimal, float, int, str],
        cost_overrun_pct: Union[Decimal, float, int, str],
        target_margin_pct: Union[Decimal, float, int, str],
    ) -> "CommercialInputs":
        """Convenience constructor accepting rates in percentage points (e.g. 10 for 10%)."""
        return cls.create(
            base_quoted_price=base_quoted_price,
            delivery_costs=delivery_costs,
            software_tooling_costs=software_tooling_costs,
            other_expenses=other_expenses,
            contingency_pct=contingency_pct,
            discount_pct=discount_pct,
            cost_overrun_pct=cost_overrun_pct,
            target_margin_pct=target_margin_pct,
            rates_as_percentages=True,
        )

    def validate(self) -> None:
        """Validate input domain rules and constraints without silent clamping."""
        # Non-negative monetary amounts
        if self.base_quoted_price < Decimal("0"):
            raise CommercialValidationError(
                f"Base quoted price cannot be negative: {self.base_quoted_price}"
            )
        if self.delivery_costs < Decimal("0"):
            raise CommercialValidationError(
                f"Delivery costs cannot be negative: {self.delivery_costs}"
            )
        if self.software_tooling_costs < Decimal("0"):
            raise CommercialValidationError(
                f"Software/tooling costs cannot be negative: {self.software_tooling_costs}"
            )
        if self.other_expenses < Decimal("0"):
            raise CommercialValidationError(
                f"Other expenses cannot be negative: {self.other_expenses}"
            )

        # Percentage boundaries
        if self.contingency_pct < Decimal("0"):
            raise CommercialValidationError(
                f"Contingency percentage cannot be negative: {self.contingency_pct}"
            )
        if self.contingency_pct > Decimal("1.0"):
            raise CommercialValidationError(
                f"Contingency percentage cannot exceed 100% (1.0); received {self.contingency_pct}"
            )

        if self.discount_pct < Decimal("0"):
            raise CommercialValidationError(
                f"Discount percentage cannot be negative: {self.discount_pct}"
            )
        if self.discount_pct > Decimal("1.0"):
            raise CommercialValidationError(
                f"Discount percentage cannot exceed 100% (1.0); received {self.discount_pct}"
            )

        if self.cost_overrun_pct < Decimal("0"):
            raise CommercialValidationError(
                f"Cost overrun percentage cannot be negative: {self.cost_overrun_pct}"
            )
        if self.cost_overrun_pct > Decimal("5.0"):
            raise CommercialValidationError(
                f"Cost overrun percentage exceeds practical boundary (500% / 5.0); received {self.cost_overrun_pct}"
            )

        if self.target_margin_pct < Decimal("0"):
            raise CommercialValidationError(
                f"Target margin percentage must be non-negative; received {self.target_margin_pct}"
            )
        if self.target_margin_pct >= Decimal("1.0"):
            raise CommercialValidationError(
                f"Target margin percentage must be strictly below 100% (< 1.0); received {self.target_margin_pct}"
            )


@dataclass(frozen=True)
class CommercialResult:
    """Comprehensive commercial outputs with unrounded Decimal precision."""

    # Cost breakdown
    direct_estimated_cost: Decimal
    contingency_amount: Decimal
    baseline_total_cost: Decimal
    scenario_delivery_cost: Decimal
    scenario_total_cost: Decimal

    # Revenue & profitability
    net_revenue: Decimal
    profit: Decimal
    profit_margin_pct: Optional[Decimal]  # In percentage points (e.g. 25.5 for 25.5%), None if net_revenue <= 0
    markup_pct: Optional[Decimal]         # In percentage points (e.g. 40.0 for 40.0%), None if total_cost <= 0

    # Advisory benchmarks
    break_even_net_revenue: Decimal
    required_net_price: Optional[Decimal]
    required_quoted_price: Optional[Decimal]

    # Health status indicators
    is_profitable: bool
    meets_target_margin: bool
    margin_gap_pct: Optional[Decimal]     # profit_margin_pct - (target_margin_pct * 100)

    def to_rounded_dict(self) -> Dict[str, Any]:
        """Return financial metrics formatted with consistent 2-decimal rounding."""
        def _round_cur(val: Optional[Decimal]) -> Optional[float]:
            if val is None:
                return None
            return float(val.quantize(CENTS_QUANTIZE, rounding=ROUND_HALF_UP))

        def _round_pct(val: Optional[Decimal]) -> Optional[float]:
            if val is None:
                return None
            return float(val.quantize(PERCENT_QUANTIZE, rounding=ROUND_HALF_UP))

        return {
            "direct_estimated_cost": _round_cur(self.direct_estimated_cost),
            "contingency_amount": _round_cur(self.contingency_amount),
            "baseline_total_cost": _round_cur(self.baseline_total_cost),
            "scenario_delivery_cost": _round_cur(self.scenario_delivery_cost),
            "scenario_total_cost": _round_cur(self.scenario_total_cost),
            "net_revenue": _round_cur(self.net_revenue),
            "profit": _round_cur(self.profit),
            "profit_margin_pct": _round_pct(self.profit_margin_pct),
            "markup_pct": _round_pct(self.markup_pct),
            "break_even_net_revenue": _round_cur(self.break_even_net_revenue),
            "required_net_price": _round_cur(self.required_net_price),
            "required_quoted_price": _round_cur(self.required_quoted_price),
            "is_profitable": self.is_profitable,
            "meets_target_margin": self.meets_target_margin,
            "margin_gap_pct": _round_pct(self.margin_gap_pct),
        }


def calculate_commercials(inputs: CommercialInputs) -> CommercialResult:
    """Execute commercial formulas defined for DealWise Phase 2.
    
    Formulas:
    1. Direct estimated cost = delivery costs + software/tooling costs + other expenses.
    2. Contingency amount = direct estimated cost * contingency percentage.
    3. Baseline total estimated cost = direct estimated cost + contingency amount.
    4. Scenario delivery cost = delivery costs * (1 + cost overrun percentage).
    5. Scenario total estimated cost = scenario delivery cost + software/tooling costs + other expenses + contingency amount.
    6. Net revenue = base quoted price * (1 - discount percentage).
    7. Profit = net revenue - scenario total estimated cost.
    8. Profit margin = profit / net revenue * 100 (when net revenue > 0).
    9. Markup = profit / scenario total estimated cost * 100 (when total cost > 0).
    10. Break-even net revenue = scenario total estimated cost.
    11. Required net price for target margin = scenario total estimated cost / (1 - target margin percentage) (target margin < 100%).
    12. Required quoted price before discount = required net price / (1 - discount percentage) (discount < 100%).
    """
    inputs.validate()

    # 1. Direct estimated cost
    direct_estimated_cost = (
        inputs.delivery_costs + inputs.software_tooling_costs + inputs.other_expenses
    )

    # 2. Contingency amount
    contingency_amount = direct_estimated_cost * inputs.contingency_pct

    # 3. Baseline total estimated cost
    baseline_total_cost = direct_estimated_cost + contingency_amount

    # 4. Scenario delivery cost
    scenario_delivery_cost = inputs.delivery_costs * (Decimal("1") + inputs.cost_overrun_pct)

    # 5. Scenario total estimated cost
    scenario_total_cost = (
        scenario_delivery_cost
        + inputs.software_tooling_costs
        + inputs.other_expenses
        + contingency_amount
    )

    # 6. Net revenue
    net_revenue = inputs.base_quoted_price * (Decimal("1") - inputs.discount_pct)

    # 7. Profit
    profit = net_revenue - scenario_total_cost

    # 8. Profit margin percentage
    profit_margin_pct: Optional[Decimal]
    if net_revenue > Decimal("0"):
        profit_margin_pct = (profit / net_revenue) * Decimal("100")
    else:
        # Zero or negative revenue cannot compute a percentage profit margin
        profit_margin_pct = None

    # 9. Markup percentage
    markup_pct: Optional[Decimal]
    if scenario_total_cost > Decimal("0"):
        markup_pct = (profit / scenario_total_cost) * Decimal("100")
    else:
        # Zero cost cannot compute a percentage markup
        markup_pct = None

    # 10. Break-even net revenue
    break_even_net_revenue = scenario_total_cost

    # 11. Required net price for a target margin
    # Provided target margin is between 0% inclusive and 100% exclusive
    margin_divisor = Decimal("1") - inputs.target_margin_pct
    if margin_divisor > Decimal("0"):
        required_net_price = scenario_total_cost / margin_divisor
    else:
        required_net_price = None

    # 12. Required quoted price before discount
    # Provided discount is below 100%
    discount_divisor = Decimal("1") - inputs.discount_pct
    if discount_divisor > Decimal("0") and required_net_price is not None:
        required_quoted_price = required_net_price / discount_divisor
    else:
        required_quoted_price = None

    # Qualitative indicators
    is_profitable = profit > Decimal("0")

    target_margin_percentage_points = inputs.target_margin_pct * Decimal("100")
    if profit_margin_pct is not None:
        meets_target_margin = profit_margin_pct >= target_margin_percentage_points
        margin_gap_pct = profit_margin_pct - target_margin_percentage_points
    else:
        meets_target_margin = False
        margin_gap_pct = None

    return CommercialResult(
        direct_estimated_cost=direct_estimated_cost,
        contingency_amount=contingency_amount,
        baseline_total_cost=baseline_total_cost,
        scenario_delivery_cost=scenario_delivery_cost,
        scenario_total_cost=scenario_total_cost,
        net_revenue=net_revenue,
        profit=profit,
        profit_margin_pct=profit_margin_pct,
        markup_pct=markup_pct,
        break_even_net_revenue=break_even_net_revenue,
        required_net_price=required_net_price,
        required_quoted_price=required_quoted_price,
        is_profitable=is_profitable,
        meets_target_margin=meets_target_margin,
        margin_gap_pct=margin_gap_pct,
    )


def format_inr(number: Union[Decimal, float, int]) -> str:
    """Format a monetary amount in Indian numbering format (e.g. ₹12,34,567.89)."""
    d = Decimal(str(number)).quantize(CENTS_QUANTIZE, rounding=ROUND_HALF_UP)
    is_negative = d < Decimal("0")
    d_abs = abs(d)

    int_part, dec_part = f"{d_abs:.2f}".split(".")

    if len(int_part) <= 3:
        formatted_int = int_part
    else:
        # Last 3 digits, then groups of 2 digits
        last_three = int_part[-3:]
        remaining = int_part[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted_int = ",".join(groups) + "," + last_three

    prefix = "-₹" if is_negative else "₹"
    return f"{prefix}{formatted_int}.{dec_part}"


def format_currency(
    val: Optional[Union[Decimal, float, int]],
    currency: str = "USD",
) -> str:
    """Format monetary numbers according to selected currency convention."""
    if val is None:
        return "N/A"

    if currency.upper() == "INR":
        return format_inr(val)

    # Standard international / USD format
    d = Decimal(str(val)).quantize(CENTS_QUANTIZE, rounding=ROUND_HALF_UP)
    is_negative = d < Decimal("0")
    d_abs = abs(d)
    prefix = "-$" if is_negative else "$"
    return f"{prefix}{d_abs:,.2f}"


def format_percentage(val: Optional[Union[Decimal, float, int]], places: int = 2) -> str:
    """Format percentage value (assumes already in percentage points, e.g. 25.5 for 25.5%)."""
    if val is None:
        return "N/A"
    quant = Decimal("1") if places == 0 else Decimal("0." + "0" * places)
    d = Decimal(str(val)).quantize(quant, rounding=ROUND_HALF_UP)
    return f"{d:.{places}f}%"

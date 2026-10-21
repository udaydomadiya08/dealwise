"""Comprehensive tests for the DealWise Phase 2 Commercial Calculation Engine."""

from decimal import Decimal
import math
import pytest
from src.commercial_engine import (
    CommercialInputs,
    CommercialResult,
    CommercialValidationError,
    calculate_commercials,
    format_currency,
    format_percentage,
)


@pytest.fixture
def baseline_inputs():
    """Hypothetical profitable consulting engagement baseline."""
    return CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="50000.00",
        software_tooling_costs="6000.00",
        other_expenses="4000.00",
        contingency_pct="0.10",     # 10%
        discount_pct="0.05",        # 5%
        cost_overrun_pct="0.00",    # 0%
        target_margin_pct="0.25",   # 25%
    )


# Test 1: Normal profitable engagement
def test_normal_profitable_engagement(baseline_inputs):
    """Verify normal profitable engagement calculations match exact formula definitions."""
    res = calculate_commercials(baseline_inputs)

    # Direct estimated cost = 50k + 6k + 4k = 60k
    assert res.direct_estimated_cost == Decimal("60000.00")
    # Contingency amount = 60k * 0.10 = 6k
    assert res.contingency_amount == Decimal("6000.00")
    # Baseline total cost = 60k + 6k = 66k
    assert res.baseline_total_cost == Decimal("66000.00")
    # Scenario delivery cost = 50k * (1 + 0) = 50k
    assert res.scenario_delivery_cost == Decimal("50000.00")
    # Scenario total cost = 50k + 6k + 4k + 6k = 66k
    assert res.scenario_total_cost == Decimal("66000.00")
    # Net revenue = 100k * (1 - 0.05) = 95k
    assert res.net_revenue == Decimal("95000.00")
    # Profit = 95k - 66k = 29k
    assert res.profit == Decimal("29000.00")
    assert res.is_profitable is True

    # Profit margin = 29,000 / 95,000 * 100 = 30.526315789...%
    rounded = res.to_rounded_dict()
    assert rounded["profit_margin_pct"] == 30.53
    # Markup = 29,000 / 66,000 * 100 = 43.939393...%
    assert rounded["markup_pct"] == 43.94
    # Break-even net revenue = 66k
    assert res.break_even_net_revenue == Decimal("66000.00")

    # Target margin meets target (30.53% >= 25%)
    assert res.meets_target_margin is True
    assert rounded["margin_gap_pct"] == 5.53


# Test 2: Loss-making engagement
def test_loss_making_engagement():
    """Verify negative profit, negative margin, and health flags for loss deals."""
    inputs = CommercialInputs.create(
        base_quoted_price="50000.00",
        delivery_costs="50000.00",
        software_tooling_costs="5000.00",
        other_expenses="5000.00",
        contingency_pct="0.10",     # $6,000 contingency
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    res = calculate_commercials(inputs)

    # Net revenue = 50k, Total cost = 60k + 6k = 66k
    # Profit = 50k - 66k = -16k
    assert res.net_revenue == Decimal("50000.00")
    assert res.scenario_total_cost == Decimal("66000.00")
    assert res.profit == Decimal("-16000.00")
    assert res.is_profitable is False
    assert res.meets_target_margin is False

    rounded = res.to_rounded_dict()
    # Profit margin = -16,000 / 50,000 * 100 = -32.0%
    assert rounded["profit_margin_pct"] == -32.00
    # Markup = -16,000 / 66,000 * 100 = -24.24%
    assert rounded["markup_pct"] == -24.24


# Test 3: Discount reducing profit and margin
def test_discount_impact():
    """Verify that increasing client discount strictly decreases net revenue, profit, and margin."""
    no_discount = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="50000.00",
        software_tooling_costs="5000.00",
        other_expenses="5000.00",
        contingency_pct="0.05",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    with_discount = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="50000.00",
        software_tooling_costs="5000.00",
        other_expenses="5000.00",
        contingency_pct="0.05",
        discount_pct="0.15", # 15% discount
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )

    res_nd = calculate_commercials(no_discount)
    res_wd = calculate_commercials(with_discount)

    assert res_nd.net_revenue == Decimal("100000.00")
    assert res_wd.net_revenue == Decimal("85000.00")
    assert res_wd.profit < res_nd.profit
    assert res_wd.profit_margin_pct < res_nd.profit_margin_pct
    # Costs must remain identical since discount only affects revenue
    assert res_wd.scenario_total_cost == res_nd.scenario_total_cost


# Test 4: Delivery-cost overrun increasing cost
def test_delivery_cost_overrun():
    """Verify cost overrun applies exclusively to delivery costs and increases scenario total cost."""
    inputs = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="50000.00",
        software_tooling_costs="6000.00",
        other_expenses="4000.00",
        contingency_pct="0.10",     # 10% of 60k = 6k
        discount_pct="0.05",
        cost_overrun_pct="0.20",    # 20% overrun on delivery costs
        target_margin_pct="0.25",
    )
    res = calculate_commercials(inputs)

    # Scenario delivery cost = 50,000 * 1.20 = 60,000
    assert res.scenario_delivery_cost == Decimal("60000.00")
    # Contingency amount remains based on direct estimated cost (6,000)
    assert res.contingency_amount == Decimal("6000.00")
    # Scenario total cost = 60k + 6k + 4k + 6k = 76,000
    assert res.scenario_total_cost == Decimal("76000.00")
    # Profit = 95,000 - 76,000 = 19,000
    assert res.profit == Decimal("19000.00")


# Test 5: Nonzero contingency calculation
def test_contingency_calculation():
    """Verify contingency amount scales accurately with direct estimated cost."""
    inputs = CommercialInputs.create(
        base_quoted_price="120000.00",
        delivery_costs="80000.00",
        software_tooling_costs="15000.00",
        other_expenses="5000.00",
        contingency_pct="0.15",     # 15%
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    res = calculate_commercials(inputs)
    # Direct = 80k + 15k + 5k = 100k
    assert res.direct_estimated_cost == Decimal("100000.00")
    # Contingency = 100k * 0.15 = 15k
    assert res.contingency_amount == Decimal("15000.00")
    assert res.baseline_total_cost == Decimal("115000.00")


# Test 6: Margin versus markup calculations
def test_margin_vs_markup_distinction():
    """Verify profit margin uses revenue as denominator, whereas markup uses cost as denominator."""
    # Cost = $50,000, Revenue = $100,000, Profit = $50,000
    inputs = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="50000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    res = calculate_commercials(inputs)

    # Margin = 50k / 100k * 100 = 50.0%
    assert res.profit_margin_pct == Decimal("50")
    # Markup = 50k / 50k * 100 = 100.0%
    assert res.markup_pct == Decimal("100")
    assert res.markup_pct > res.profit_margin_pct


# Test 7: Target-margin pricing formula
def test_target_margin_pricing():
    """Verify required net price correctly yields target margin when plugged back into formula."""
    inputs = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="60000.00",
        software_tooling_costs="10000.00",
        other_expenses="5000.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.25",   # 25% target margin
    )
    res = calculate_commercials(inputs)
    # Total cost = 75,000
    # Required net price = 75,000 / (1 - 0.25) = 75,000 / 0.75 = 100,000.00
    assert res.scenario_total_cost == Decimal("75000.00")
    assert res.required_net_price == Decimal("100000.00")

    # If revenue is 100k, margin is exactly (100k - 75k) / 100k = 25%
    test_plug = CommercialInputs.create(
        base_quoted_price=res.required_net_price,
        delivery_costs="60000.00",
        software_tooling_costs="10000.00",
        other_expenses="5000.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.25",
    )
    plug_res = calculate_commercials(test_plug)
    assert plug_res.profit_margin_pct == Decimal("25")


# Test 8: Required quoted price when discount applies
def test_required_quoted_price_with_discount():
    """Verify required quoted price accounts for both target margin and client discount."""
    # Total cost = 75,000, Target margin = 25% -> Required net price = 100,000
    # Discount = 20% -> Required quoted price = 100,000 / (1 - 0.20) = 125,000.00
    inputs = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="75000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.20",        # 20% discount
        cost_overrun_pct="0.00",
        target_margin_pct="0.25",   # 25% target margin
    )
    res = calculate_commercials(inputs)
    assert res.required_net_price == Decimal("100000.00")
    assert res.required_quoted_price == Decimal("125000.00")

    # Plug required quoted price back in:
    plug = CommercialInputs.create(
        base_quoted_price=res.required_quoted_price,
        delivery_costs="75000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.20",
        cost_overrun_pct="0.00",
        target_margin_pct="0.25",
    )
    plug_res = calculate_commercials(plug)
    assert plug_res.net_revenue == Decimal("100000.00")
    assert plug_res.profit_margin_pct == Decimal("25")


# Test 9: Zero revenue edge case
def test_zero_revenue_edge_case():
    """Verify zero revenue does not raise ZeroDivisionError and sets margin to None."""
    inputs = CommercialInputs.create(
        base_quoted_price="0.00",
        delivery_costs="40000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    res = calculate_commercials(inputs)

    assert res.net_revenue == Decimal("0.00")
    assert res.profit == Decimal("-40000.00")
    # Margin must be explicitly None, never NaN or Inf
    assert res.profit_margin_pct is None
    # Markup is (-40k / 40k) * 100 = -100%
    assert res.markup_pct == Decimal("-100")
    assert res.is_profitable is False


# Test 10: Zero cost edge case
def test_zero_cost_edge_case():
    """Verify zero cost handles markup division by zero gracefully."""
    inputs = CommercialInputs.create(
        base_quoted_price="50000.00",
        delivery_costs="0.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    res = calculate_commercials(inputs)

    assert res.scenario_total_cost == Decimal("0.00")
    assert res.profit == Decimal("50000.00")
    assert res.profit_margin_pct == Decimal("100")
    # Markup must be explicitly None (division by zero cost)
    assert res.markup_pct is None
    assert res.break_even_net_revenue == Decimal("0.00")
    assert res.required_net_price == Decimal("0.00")


# Test 11: Invalid negative costs or prices
@pytest.mark.parametrize(
    "field,kwargs",
    [
        ("base_quoted_price", {"base_quoted_price": "-100.00"}),
        ("delivery_costs", {"delivery_costs": "-500.00"}),
        ("software_tooling_costs", {"software_tooling_costs": "-50.00"}),
        ("other_expenses", {"other_expenses": "-10.00"}),
    ],
)
def test_invalid_negative_costs_or_prices(field, kwargs):
    """Ensure negative financial amounts raise CommercialValidationError."""
    defaults = {
        "base_quoted_price": "100000.00",
        "delivery_costs": "50000.00",
        "software_tooling_costs": "5000.00",
        "other_expenses": "2000.00",
        "contingency_pct": "0.10",
        "discount_pct": "0.05",
        "cost_overrun_pct": "0.00",
        "target_margin_pct": "0.20",
    }
    defaults.update(kwargs)
    with pytest.raises(CommercialValidationError) as excinfo:
        CommercialInputs.create(**defaults)
    assert "cannot be negative" in str(excinfo.value)


# Test 12: Invalid percentage inputs & non-finite numbers
@pytest.mark.parametrize(
    "kwargs,err_text",
    [
        ({"contingency_pct": "-0.05"}, "cannot be negative"),
        ({"contingency_pct": "1.50"}, "cannot exceed 100%"),
        ({"discount_pct": "-0.10"}, "cannot be negative"),
        ({"discount_pct": "1.10"}, "cannot exceed 100%"),
        ({"cost_overrun_pct": "-0.01"}, "cannot be negative"),
        ({"cost_overrun_pct": "6.00"}, "exceeds practical boundary"),
        ({"target_margin_pct": "-0.05"}, "must be non-negative"),
        ({"target_margin_pct": "1.00"}, "must be strictly below 100%"),
        ({"target_margin_pct": "1.25"}, "must be strictly below 100%"),
        ({"base_quoted_price": float("nan")}, "must be a finite number"),
        ({"delivery_costs": float("inf")}, "must be a finite number"),
    ],
)
def test_invalid_percentage_and_non_finite_inputs(kwargs, err_text):
    """Ensure out-of-range percentages and non-finite floats are cleanly rejected."""
    defaults = {
        "base_quoted_price": "100000.00",
        "delivery_costs": "50000.00",
        "software_tooling_costs": "5000.00",
        "other_expenses": "2000.00",
        "contingency_pct": "0.10",
        "discount_pct": "0.05",
        "cost_overrun_pct": "0.00",
        "target_margin_pct": "0.20",
    }
    defaults.update(kwargs)
    with pytest.raises(CommercialValidationError) as excinfo:
        CommercialInputs.create(**defaults)
    assert err_text in str(excinfo.value)


# Test 13: Values at percentage boundaries
def test_percentage_boundaries():
    """Verify exact behavior at 0%, 100% discount, and 0% target margin."""
    # 0% discount and 0% target margin
    inputs = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="60000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.00",   # 0% target margin is valid
    )
    res = calculate_commercials(inputs)
    assert res.required_net_price == Decimal("60000.00")
    assert res.required_quoted_price == Decimal("60000.00")

    # 100% discount boundary (1.0)
    disc_100 = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="50000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="1.00",        # 100% discount
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    res_100 = calculate_commercials(disc_100)
    assert res_100.net_revenue == Decimal("0.00")
    assert res_100.profit == Decimal("-50000.00")
    # With 100% discount, required quoted price before discount cannot be computed
    assert res_100.required_quoted_price is None


# Test 14: Reproducible calculations for identical inputs
def test_reproducible_calculations(baseline_inputs):
    """Verify deterministic, identical outputs across repeated execution runs."""
    res1 = calculate_commercials(baseline_inputs)
    res2 = calculate_commercials(baseline_inputs)
    assert res1 == res2
    assert res1.to_rounded_dict() == res2.to_rounded_dict()


# Test helper: Currency formatting
def test_currency_formatting():
    """Verify INR and USD currency formatting conventions."""
    assert format_currency(Decimal("100000.50"), "USD") == "$100,000.50"
    assert format_currency(Decimal("-25000.00"), "USD") == "-$25,000.00"
    assert format_currency(Decimal("1234567.89"), "INR") == "₹12,34,567.89"
    assert format_currency(Decimal("-50000.00"), "INR") == "-₹50,000.00"
    assert format_currency(None, "USD") == "N/A"


def test_percentage_formatting():
    """Verify percentage formatting."""
    assert format_percentage(Decimal("30.526"), places=2) == "30.53%"
    assert format_percentage(Decimal("-12.5"), places=1) == "-12.5%"
    assert format_percentage(None) == "N/A"

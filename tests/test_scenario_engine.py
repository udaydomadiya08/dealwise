"""Unit tests for Phase 4 Scenario Analysis Engine, sensitivity grids, and contract models."""

import csv
from decimal import Decimal
import io
import pytest

from src.commercial_engine import CommercialInputs, CommercialValidationError
from src.scenario_engine import (
    ScenarioComparison,
    compare_scenarios,
    generate_sensitivity_grid,
    evaluate_fixed_fee_model,
    evaluate_time_and_materials_model,
    export_scenario_to_csv,
)


@pytest.fixture
def standard_baseline():
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


# 1. Unchanged inputs reproduce baseline results
def test_unchanged_inputs_reproduce_baseline(standard_baseline):
    """Verify comparing identical inputs results in zero deltas across all metrics."""
    comp = compare_scenarios(standard_baseline, standard_baseline)

    assert comp.delta_net_revenue == Decimal("0.00")
    assert comp.delta_total_cost == Decimal("0.00")
    assert comp.delta_profit == Decimal("0.00")
    assert comp.delta_margin_percentage_points == Decimal("0.00")
    assert comp.delta_markup_percentage_points == Decimal("0.00")
    assert comp.scenario_is_profitable == comp.baseline_result.is_profitable
    assert comp.scenario_meets_target == comp.baseline_result.meets_target_margin


# 2. A discount reduces revenue and cannot improve profit
def test_discount_reduces_revenue_and_profit(standard_baseline):
    """Verify that increasing client discount strictly reduces net revenue and profit."""
    discounted_scenario = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="50000.00",
        software_tooling_costs="6000.00",
        other_expenses="4000.00",
        contingency_pct="0.10",
        discount_pct="0.15", # increased from 5% to 15%
        cost_overrun_pct="0.00",
        target_margin_pct="0.25",
    )
    comp = compare_scenarios(standard_baseline, discounted_scenario)

    # 10% more discount on 100k reduces revenue by exactly 10,000
    assert comp.delta_net_revenue == Decimal("-10000.00")
    assert comp.delta_total_cost == Decimal("0.00")
    assert comp.delta_profit == Decimal("-10000.00")
    assert comp.scenario_result.profit < comp.baseline_result.profit


# 3. Delivery-cost overrun increases total cost and cannot improve profit
def test_cost_overrun_increases_cost_and_reduces_profit(standard_baseline):
    """Verify cost overrun increases cost and reduces profit while revenue is unchanged."""
    overrun_scenario = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="50000.00",
        software_tooling_costs="6000.00",
        other_expenses="4000.00",
        contingency_pct="0.10",
        discount_pct="0.05",
        cost_overrun_pct="0.20", # 20% overrun on 50k delivery = 10k additional cost
        target_margin_pct="0.25",
    )
    comp = compare_scenarios(standard_baseline, overrun_scenario)

    assert comp.delta_net_revenue == Decimal("0.00")
    assert comp.delta_total_cost == Decimal("10000.00")
    assert comp.delta_profit == Decimal("-10000.00")
    assert comp.scenario_result.profit < comp.baseline_result.profit


# 4. Profit changes reconcile with revenue and cost changes
def test_profit_reconciliation_identity(standard_baseline):
    """Verify mathematical identity: delta_profit == delta_net_revenue - delta_total_cost."""
    multi_delta_scenario = CommercialInputs.create(
        base_quoted_price="120000.00", # +20k base
        delivery_costs="60000.00",     # +10k delivery
        software_tooling_costs="8000.00",
        other_expenses="2000.00",
        contingency_pct="0.15",
        discount_pct="0.10",
        cost_overrun_pct="0.10",
        target_margin_pct="0.25",
    )
    comp = compare_scenarios(standard_baseline, multi_delta_scenario)

    expected_delta_profit = comp.delta_net_revenue - comp.delta_total_cost
    assert comp.delta_profit == expected_delta_profit


# 5. Margin changes use percentage-point arithmetic
def test_margin_delta_percentage_points():
    """Verify margin change is expressed in percentage points (pp), not relative percentage change."""
    # Baseline: 100k revenue, 70k cost -> 30k profit -> 30.0% margin
    base = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="70000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.25",
    )
    # Scenario: 100k revenue, 75k cost -> 25k profit -> 25.0% margin
    scen = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="75000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.25",
    )
    comp = compare_scenarios(base, scen)

    # Margin moves from 30.0% to 25.0% -> difference is exactly -5.0 percentage points
    assert comp.delta_margin_percentage_points == Decimal("-5.00")


# 6. Sensitivity grid contains the expected number of valid cases
def test_sensitivity_grid_dimensions_and_values(standard_baseline):
    """Verify grid shape, cell count, and calculation validity."""
    discounts = ["0.0", "5.0", "10.0"]
    overruns = ["0.0", "10.0", "20.0", "30.0"]

    grid = generate_sensitivity_grid(standard_baseline, discounts, overruns, rates_as_percentages=True)

    assert len(grid) == 4 # 4 overrun rows
    for row in grid:
        assert len(row) == 3 # 3 discount columns
        for cell in row:
            assert cell.net_revenue > 0
            assert cell.total_cost > 0
            assert cell.profit == cell.net_revenue - cell.total_cost


# 7. Zero-revenue and zero-cost boundaries
def test_scenario_zero_revenue_and_zero_cost_boundaries():
    """Verify scenario comparison handles zero revenue and zero cost gracefully without NaN."""
    zero_rev_scen = CommercialInputs.create(
        base_quoted_price="0.00",
        delivery_costs="50000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    normal = CommercialInputs.create(
        base_quoted_price="100000.00",
        delivery_costs="50000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )

    comp = compare_scenarios(normal, zero_rev_scen)
    assert comp.scenario_result.profit_margin_pct is None
    # When scenario margin is None, delta_margin_percentage_points is None
    assert comp.delta_margin_percentage_points is None


# 8. Invalid inputs are rejected
@pytest.mark.parametrize(
    "fee,deliv,soft,cont,overrun",
    [
        ("-100.00", "50000.00", "5000.00", "10.0", "0.0"),
        ("100000.00", "-500.00", "5000.00", "10.0", "0.0"),
        ("100000.00", "50000.00", "-50.00", "10.0", "0.0"),
        ("100000.00", "50000.00", "5000.00", "-5.0", "0.0"),
        ("100000.00", "50000.00", "5000.00", "150.0", "0.0"), # contingency > 100%
        ("100000.00", "50000.00", "5000.00", "10.0", "-5.0"),
    ],
)
def test_fixed_fee_invalid_inputs_rejected(fee, deliv, soft, cont, overrun):
    """Verify invalid inputs in fixed fee model are rejected with CommercialValidationError."""
    with pytest.raises(CommercialValidationError):
        evaluate_fixed_fee_model(fee, deliv, soft, cont, overrun)


# 9. Fixed Fee model calculations
def test_fixed_fee_evaluation():
    """Verify Fixed Fee calculation under standard and overrun scenarios."""
    eval_std = evaluate_fixed_fee_model(
        agreed_fixed_fee="100000.00",
        delivery_costs="50000.00",
        software_and_expenses="10000.00",
        contingency_pct="10.0",  # direct = 60k, cont = 6k, total = 66k
        cost_overrun_pct="0.0",
    )
    assert eval_std.revenue == Decimal("100000.00")
    assert eval_std.total_cost == Decimal("66000.00")
    assert eval_std.profit == Decimal("34000.00")
    assert eval_std.profit_margin_pct == Decimal("34.00")

    # With 20% labor overrun (50k * 1.2 = 60k labor -> total cost = 60k + 10k + 6k = 76k)
    eval_overrun = evaluate_fixed_fee_model(
        agreed_fixed_fee="100000.00",
        delivery_costs="50000.00",
        software_and_expenses="10000.00",
        contingency_pct="10.0",
        cost_overrun_pct="20.0",
    )
    assert eval_overrun.total_cost == Decimal("76000.00")
    assert eval_overrun.profit == Decimal("24000.00")
    assert eval_overrun.profit_margin_pct == Decimal("24.00")


# 10. Time & Materials calculations
def test_time_and_materials_evaluation():
    """Verify Time & Materials calculation where billable hours drive revenue and cost separately."""
    eval_tm = evaluate_time_and_materials_model(
        billable_hours="500.0",
        billing_rate_per_hour="200.00",   # revenue = 500 * 200 = 100,000
        cost_rate_per_hour="100.00",      # labor cost = 500 * 100 = 50,000
        software_and_expenses="10000.00", # direct = 60,000
        contingency_pct="0.0",
        hours_overrun_pct="0.0",
    )
    assert eval_tm.revenue == Decimal("100000.00")
    assert eval_tm.total_cost == Decimal("60000.00")
    assert eval_tm.profit == Decimal("40000.00")
    assert eval_tm.profit_margin_pct == Decimal("40.00")
    assert eval_tm.markup_pct == Decimal("66.66666666666666666666666667")

    # Under T&M with 20% hours overrun (600 hours):
    # revenue = 600 * 200 = 120,000
    # labor cost = 600 * 100 = 60,000 + 10k expenses = 70,000
    # profit = 120k - 70k = 50,000 (profit expands because client pays for hours!)
    eval_tm_overrun = evaluate_time_and_materials_model(
        billable_hours="500.0",
        billing_rate_per_hour="200.00",
        cost_rate_per_hour="100.00",
        software_and_expenses="10000.00",
        contingency_pct="0.0",
        hours_overrun_pct="20.0",
    )
    assert eval_tm_overrun.revenue == Decimal("120000.00")
    assert eval_tm_overrun.total_cost == Decimal("70000.00")
    assert eval_tm_overrun.profit == Decimal("50000.00")


# 11. CSV data export format and usability
def test_csv_export_format(standard_baseline):
    """Verify generated CSV contains all sections, valid numeric fields, and no errors."""
    scen = CommercialInputs.create(
        base_quoted_price="90000.00",
        delivery_costs="55000.00",
        software_tooling_costs="6000.00",
        other_expenses="4000.00",
        contingency_pct="0.10",
        discount_pct="0.10",
        cost_overrun_pct="0.05",
        target_margin_pct="0.25",
    )
    comp = compare_scenarios(standard_baseline, scen)
    grid = generate_sensitivity_grid(standard_baseline, ["0.0", "10.0"], ["0.0", "10.0"])

    csv_text = export_scenario_to_csv(comp, grid, "USD")

    assert "DEALWISE SCENARIO SIMULATION & SENSITIVITY REPORT" in csv_text
    assert "SECTION 1: PROPOSAL INPUT PARAMETERS" in csv_text
    assert "SECTION 2: FINANCIAL OUTPUTS & DELTAS" in csv_text
    assert "SECTION 3: SENSITIVITY GRID MATRIX" in csv_text

    # Parse with Python csv module to confirm valid CSV syntax
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)
    assert len(rows) > 15

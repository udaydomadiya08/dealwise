"""Unit tests for Phase 3 Executive Dashboard analytics and visualization helpers."""

from decimal import Decimal
import pytest
from src.commercial_engine import CommercialInputs, calculate_commercials
from src.dashboard import (
    assess_commercial_health,
    get_cost_composition,
    build_revenue_vs_cost_chart,
    build_cost_composition_chart,
    build_profitability_benchmark_chart,
)


@pytest.fixture
def sample_deal_inputs():
    """Standard profitable advisory engagement inputs."""
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


def test_health_report_profitable_deal(sample_deal_inputs):
    """Verify health report accurately identifies profitable engagement exceeding target margin."""
    result = calculate_commercials(sample_deal_inputs)
    health = assess_commercial_health(result, sample_deal_inputs.target_margin_pct)

    assert health.profitability_status == "Profitable"
    assert health.is_profitable is True
    assert health.margin_target_status == "Target Margin Met"
    assert health.meets_target_margin is True
    assert health.is_above_break_even is True
    assert health.break_even_difference == Decimal("29000.00")
    assert "Profit Margin is 30.53%" in health.margin_vs_markup_summary
    assert "Markup is 43.94%" in health.margin_vs_markup_summary
    assert "satisfies practice target threshold" in health.executive_narrative


def test_health_report_loss_making_deal():
    """Verify health report identifies loss-making engagement and deficit to break-even."""
    loss_inputs = CommercialInputs.create(
        base_quoted_price="50000.00",
        delivery_costs="50000.00",
        software_tooling_costs="5000.00",
        other_expenses="5000.00",
        contingency_pct="0.10",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    result = calculate_commercials(loss_inputs)
    health = assess_commercial_health(result, loss_inputs.target_margin_pct)

    assert health.profitability_status == "Loss-Making"
    assert health.is_profitable is False
    assert health.margin_target_status == "Projected Margin Below Target"
    assert health.meets_target_margin is False
    assert health.is_above_break_even is False
    assert health.break_even_difference == Decimal("-16000.00")
    assert "deficit" in health.executive_narrative


def test_health_report_margin_below_target():
    """Verify health report for a deal that is profitable but below target margin."""
    inputs = CommercialInputs.create(
        base_quoted_price="80000.00",
        delivery_costs="50000.00",
        software_tooling_costs="6000.00",
        other_expenses="4000.00",
        contingency_pct="0.10", # cost = 66,000
        discount_pct="0.00",    # net revenue = 80,000 -> profit = 14,000, margin = 17.5%
        cost_overrun_pct="0.00",
        target_margin_pct="0.25", # target = 25%
    )
    result = calculate_commercials(inputs)
    health = assess_commercial_health(result, inputs.target_margin_pct)

    assert health.profitability_status == "Profitable"
    assert health.is_profitable is True
    assert health.margin_target_status == "Projected Margin Below Target"
    assert health.meets_target_margin is False
    assert health.is_above_break_even is True
    assert "Projected margin below practice target" in health.executive_narrative


def test_cost_composition_reconciliation(sample_deal_inputs):
    """Verify cost components sum exactly to scenario_total_cost with overrun."""
    overrun_inputs = CommercialInputs.create(
        base_quoted_price="120000.00",
        delivery_costs="50000.00",
        software_tooling_costs="8000.00",
        other_expenses="2000.00",
        contingency_pct="0.10",
        discount_pct="0.00",
        cost_overrun_pct="0.15", # 15% overrun on delivery labor
        target_margin_pct="0.25",
    )
    result = calculate_commercials(overrun_inputs)
    composition = get_cost_composition(overrun_inputs, result)

    total_from_components = sum(item["amount"] for item in composition)
    assert total_from_components == result.scenario_total_cost
    assert any("Overrun" in item["category"] for item in composition)


def test_charts_profitable_deal(sample_deal_inputs):
    """Verify Plotly charts build successfully for standard profitable engagement."""
    result = calculate_commercials(sample_deal_inputs)

    fig1 = build_revenue_vs_cost_chart(result, "USD")
    assert fig1 is not None
    assert len(fig1.data) == 1
    assert fig1.data[0].x[0] == "Net Revenue"

    fig2 = build_cost_composition_chart(sample_deal_inputs, result, "USD")
    assert fig2 is not None
    assert len(fig2.data) == 1

    fig3 = build_profitability_benchmark_chart(result, sample_deal_inputs.target_margin_pct)
    assert fig3 is not None
    assert len(fig3.data) == 1


def test_charts_loss_making_deal():
    """Verify charts handle negative profit without error or broken data."""
    loss_inputs = CommercialInputs.create(
        base_quoted_price="40000.00",
        delivery_costs="50000.00",
        software_tooling_costs="5000.00",
        other_expenses="5000.00",
        contingency_pct="0.10",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    result = calculate_commercials(loss_inputs)
    assert result.profit < 0

    fig1 = build_revenue_vs_cost_chart(result, "USD")
    assert "Projected Loss" in fig1.data[0].x
    # Profit value in chart matches negative profit
    assert fig1.data[0].y[2] == float(result.profit)

    fig2 = build_cost_composition_chart(loss_inputs, result, "USD")
    assert fig2 is not None

    fig3 = build_profitability_benchmark_chart(result, loss_inputs.target_margin_pct)
    assert fig3 is not None


def test_charts_zero_revenue_and_zero_cost():
    """Verify zero revenue and zero cost edge cases generate valid chart data without crash."""
    # Zero revenue
    zero_rev_inputs = CommercialInputs.create(
        base_quoted_price="0.00",
        delivery_costs="30000.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    res_zero_rev = calculate_commercials(zero_rev_inputs)
    fig_rev = build_revenue_vs_cost_chart(res_zero_rev, "USD")
    assert fig_rev is not None
    fig_bench = build_profitability_benchmark_chart(res_zero_rev, zero_rev_inputs.target_margin_pct)
    assert fig_bench is not None

    # Zero cost
    zero_cost_inputs = CommercialInputs.create(
        base_quoted_price="50000.00",
        delivery_costs="0.00",
        software_tooling_costs="0.00",
        other_expenses="0.00",
        contingency_pct="0.00",
        discount_pct="0.00",
        cost_overrun_pct="0.00",
        target_margin_pct="0.20",
    )
    res_zero_cost = calculate_commercials(zero_cost_inputs)
    fig_cost = build_cost_composition_chart(zero_cost_inputs, res_zero_cost, "USD")
    assert fig_cost is not None


def test_currency_formatting_in_charts(sample_deal_inputs):
    """Verify charts use specified currency string in axis titles and annotations."""
    result = calculate_commercials(sample_deal_inputs)

    fig_inr = build_revenue_vs_cost_chart(result, "INR")
    assert "INR" in fig_inr.layout.yaxis.title.text

    fig_usd = build_revenue_vs_cost_chart(result, "USD")
    assert "USD" in fig_usd.layout.yaxis.title.text

"""Executive Dashboard analytics, health assessment, and data visualization helpers.

Phase 3: Business intelligence layer bridging the commercial engine and UI.
Independent of Streamlit rendering so it can be thoroughly tested via Pytest.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional
import plotly.graph_objects as go
from src.commercial_engine import (
    CommercialInputs,
    CommercialResult,
    format_currency,
    format_percentage,
)


@dataclass(frozen=True)
class CommercialHealthReport:
    """Accessible, qualitative executive assessment of commercial health."""

    profitability_status: str          # "Profitable", "Loss-Making", "Break-Even"
    is_profitable: bool
    margin_target_status: str          # "Target Margin Met", "Projected Margin Below Target", "Zero Revenue Undefined"
    meets_target_margin: bool
    break_even_difference: Decimal     # Net Revenue - Break-Even Net Revenue (positive = surplus, negative = shortfall)
    is_above_break_even: bool
    margin_vs_markup_summary: str      # Clear distinction for this engagement
    executive_narrative: str           # Objective, non-guaranteed advisory statement


def assess_commercial_health(
    result: CommercialResult,
    target_margin_rate: Decimal,  # Fractional rate, e.g. 0.25 for 25%
) -> CommercialHealthReport:
    """Produce an objective, carefully worded commercial health assessment.
    
    Never claims 'safe' or 'guaranteed' profitability. Handles zero-revenue and zero-cost edge cases.
    """
    target_margin_pct_val = target_margin_rate * Decimal("100")

    # 1. Profitability status
    if result.profit > Decimal("0"):
        profitability_status = "Profitable"
        is_profitable = True
    elif result.profit < Decimal("0"):
        profitability_status = "Loss-Making"
        is_profitable = False
    else:
        profitability_status = "Break-Even"
        is_profitable = False

    # 2. Margin target status
    if result.profit_margin_pct is None:
        margin_target_status = "Zero Revenue Undefined"
        meets_target_margin = False
    elif result.profit_margin_pct >= target_margin_pct_val:
        margin_target_status = "Target Margin Met"
        meets_target_margin = True
    else:
        margin_target_status = "Projected Margin Below Target"
        meets_target_margin = False

    # 3. Break-even difference
    # Break-even net revenue = scenario_total_cost
    # difference = net_revenue - break_even_net_revenue = profit
    break_even_diff = result.net_revenue - result.break_even_net_revenue
    is_above_break_even = break_even_diff > Decimal("0")

    # 4. Margin vs Markup explanation
    if result.profit_margin_pct is not None and result.markup_pct is not None:
        margin_str = format_percentage(result.profit_margin_pct)
        markup_str = format_percentage(result.markup_pct)
        margin_vs_markup = (
            f"Profit Margin is {margin_str} (fee retained as profit, using Net Revenue as denominator), "
            f"while Markup is {markup_str} (profit added over cost, using Total Cost as denominator)."
        )
    elif result.profit_margin_pct is None and result.markup_pct is not None:
        margin_vs_markup = (
            "Profit Margin is undefined because Net Revenue is zero. "
            f"Markup is {format_percentage(result.markup_pct)}."
        )
    elif result.profit_margin_pct is not None and result.markup_pct is None:
        margin_vs_markup = (
            f"Profit Margin is {format_percentage(result.profit_margin_pct)}. "
            "Markup is undefined because total estimated delivery cost is zero."
        )
    else:
        margin_vs_markup = "Both Profit Margin and Markup are undefined because both revenue and cost are zero."

    # 5. Executive narrative with cautious, professional wording
    if not is_profitable:
        executive_narrative = (
            "Projected engagement operates at an estimated deficit. Net revenue is insufficient "
            "to cover modeled delivery, software, overhead, and contingency costs. Commercial restructuring "
            "or price recalibration is recommended prior to proposal submission."
        )
    elif not meets_target_margin:
        executive_narrative = (
            "Projected margin below practice target threshold. While the engagement shows a positive operating "
            "profit above break-even, the current fee structure does not meet standard target profitability guidelines."
        )
    else:
        executive_narrative = (
            "Projected margin satisfies practice target threshold under current assumptions. Continued delivery "
            "governance and scope control are required during execution to prevent margin erosion."
        )

    return CommercialHealthReport(
        profitability_status=profitability_status,
        is_profitable=is_profitable,
        margin_target_status=margin_target_status,
        meets_target_margin=meets_target_margin,
        break_even_difference=break_even_diff,
        is_above_break_even=is_above_break_even,
        margin_vs_markup_summary=margin_vs_markup,
        executive_narrative=executive_narrative,
    )


def get_cost_composition(
    inputs: CommercialInputs,
    result: CommercialResult,
) -> List[Dict[str, Any]]:
    """Return reconciled cost categories that strictly sum to scenario_total_cost."""
    base_delivery = inputs.delivery_costs
    overrun_amount = result.scenario_delivery_cost - inputs.delivery_costs
    software = inputs.software_tooling_costs
    other = inputs.other_expenses
    contingency = result.contingency_amount

    # Verification: base_delivery + overrun + software + other + contingency == scenario_total_cost
    reconciled_sum = base_delivery + overrun_amount + software + other + contingency
    if reconciled_sum != result.scenario_total_cost:
        raise ValueError(
            f"Cost composition reconciliation error: sum ({reconciled_sum}) != total ({result.scenario_total_cost})"
        )

    items = [
        {
            "category": "Direct Labor & Subcontractors (Base)",
            "amount": base_delivery,
            "description": "Baseline labor and delivery specialist costs",
        },
    ]

    if overrun_amount > Decimal("0"):
        items.append({
            "category": "Labor Cost Overrun (Scenario)",
            "amount": overrun_amount,
            "description": f"Modeled {format_percentage(inputs.cost_overrun_pct * Decimal('100'))} delivery overrun impact",
        })

    items.extend([
        {
            "category": "Software & Cloud Tooling",
            "amount": software,
            "description": "SaaS licenses, compute resources, and tooling",
        },
        {
            "category": "Other Project Expenses",
            "amount": other,
            "description": "Travel, logistics, and delivery incidental costs",
        },
        {
            "category": "Contingency Reserve",
            "amount": contingency,
            "description": f"{format_percentage(inputs.contingency_pct * Decimal('100'))} buffer on direct costs",
        },
    ])

    return items


def build_revenue_vs_cost_chart(
    result: CommercialResult,
    currency: str = "USD",
) -> go.Figure:
    """Build comparative bar chart showing Net Revenue, Estimated Cost, and Profit/Loss."""
    fig = go.Figure()

    is_loss = result.profit < Decimal("0")
    profit_color = "#DC2626" if is_loss else "#16A34A"
    profit_label = "Projected Loss" if is_loss else "Projected Profit"

    x_labels = ["Net Revenue", "Scenario Total Cost", profit_label]
    y_values = [
        float(result.net_revenue),
        float(result.scenario_total_cost),
        float(result.profit),
    ]
    bar_colors = ["#1E3A8A", "#64748B", profit_color]
    text_labels = [
        format_currency(result.net_revenue, currency),
        format_currency(result.scenario_total_cost, currency),
        format_currency(result.profit, currency),
    ]

    fig.add_trace(
        go.Bar(
            x=x_labels,
            y=y_values,
            marker_color=bar_colors,
            text=text_labels,
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Amount: %{text}<extra></extra>",
        )
    )

    # Reference break-even line if cost > 0
    if result.scenario_total_cost > Decimal("0"):
        fig.add_hline(
            y=float(result.scenario_total_cost),
            line_dash="dash",
            line_color="#94A3B8",
            annotation_text=f"Break-Even Level ({format_currency(result.scenario_total_cost, currency)})",
            annotation_position="top left",
            annotation_font_size=10,
            annotation_font_color="#475569",
        )

    fig.update_layout(
        title={
            "text": "Revenue vs. Delivery Cost & Operating Profit",
            "font": {"size": 14, "color": "#1E293B"},
        },
        height=320,
        margin=dict(l=20, r=20, t=45, b=25),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        yaxis=dict(
            title=f"Amount ({currency})",
            showgrid=True,
            gridcolor="#F1F5F9",
            zeroline=True,
            zerolinecolor="#94A3B8",
            zerolinewidth=1.5,
        ),
        xaxis=dict(
            tickfont=dict(size=11, color="#334155"),
            showgrid=False,
        ),
        showlegend=False,
    )
    return fig


def build_cost_composition_chart(
    inputs: CommercialInputs,
    result: CommercialResult,
    currency: str = "USD",
) -> go.Figure:
    """Build horizontal stacked/sorted bar chart of all cost components reconciling to total."""
    composition = get_cost_composition(inputs, result)

    categories = [item["category"] for item in composition]
    amounts = [float(item["amount"]) for item in composition]
    texts = [format_currency(item["amount"], currency) for item in composition]

    # Palette of corporate blues/slates/amber
    palette = ["#1E3A8A", "#EF4444", "#2563EB", "#60A5FA", "#F59E0B"]
    colors = palette[: len(categories)]

    fig = go.Figure(
        go.Bar(
            y=categories,
            x=amounts,
            orientation="h",
            marker_color=colors,
            text=texts,
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>Component: %{text}<extra></extra>",
        )
    )

    total_str = format_currency(result.scenario_total_cost, currency)
    fig.update_layout(
        title={
            "text": f"Cost Composition (Total: {total_str})",
            "font": {"size": 14, "color": "#1E293B"},
        },
        height=320,
        margin=dict(l=20, r=20, t=45, b=25),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(
            title=f"Amount ({currency})",
            showgrid=True,
            gridcolor="#F1F5F9",
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=11, color="#334155"),
        ),
        showlegend=False,
    )
    return fig


def build_profitability_benchmark_chart(
    result: CommercialResult,
    target_margin_rate: Decimal,
) -> go.Figure:
    """Build comparative rate benchmark chart: Projected Margin vs. Target Margin vs. Markup."""
    target_margin_pct_val = float(target_margin_rate * Decimal("100"))
    actual_margin_val = float(result.profit_margin_pct) if result.profit_margin_pct is not None else 0.0
    markup_val = float(result.markup_pct) if result.markup_pct is not None else 0.0

    categories = ["Projected Profit Margin", "Target Practice Margin", "Markup on Cost"]
    values = [actual_margin_val, target_margin_pct_val, markup_val]

    # Margin color logic
    if result.profit_margin_pct is None:
        margin_color = "#94A3B8"
    elif actual_margin_val >= target_margin_pct_val:
        margin_color = "#16A34A"
    elif actual_margin_val > 0:
        margin_color = "#D97706"
    else:
        margin_color = "#DC2626"

    bar_colors = [margin_color, "#2563EB", "#64748B"]
    text_labels = [
        format_percentage(result.profit_margin_pct),
        format_percentage(target_margin_pct_val),
        format_percentage(result.markup_pct),
    ]

    fig = go.Figure(
        go.Bar(
            x=categories,
            y=values,
            marker_color=bar_colors,
            text=text_labels,
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Rate: %{text}<extra></extra>",
        )
    )

    # Reference line at target margin
    fig.add_hline(
        y=target_margin_pct_val,
        line_dash="dot",
        line_color="#2563EB",
        annotation_text=f"Target Margin ({format_percentage(target_margin_pct_val)})",
        annotation_position="top right",
        annotation_font_size=10,
        annotation_font_color="#1E40AF",
    )

    fig.update_layout(
        title={
            "text": "Profitability & Margin Benchmarks",
            "font": {"size": 14, "color": "#1E293B"},
        },
        height=320,
        margin=dict(l=20, r=20, t=45, b=25),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        yaxis=dict(
            title="Percentage (%)",
            showgrid=True,
            gridcolor="#F1F5F9",
            zeroline=True,
            zerolinecolor="#94A3B8",
            zerolinewidth=1.5,
        ),
        xaxis=dict(
            tickfont=dict(size=11, color="#334155"),
            showgrid=False,
        ),
        showlegend=False,
    )
    return fig


def build_sensitivity_heatmap(
    grid: List[List[Any]],
    currency: str = "USD",
    metric: str = "margin",
) -> go.Figure:
    """Build an annotated 2D heatmap matrix across discount and delivery overrun variations."""
    if not grid or not grid[0]:
        return go.Figure()

    # Extract axes
    x_discounts = [f"{cell.discount_pct * Decimal('100'):.1f}%" for cell in grid[0]]
    y_overruns = [f"{row[0].cost_overrun_pct * Decimal('100'):.1f}%" for row in grid]

    z_values: List[List[Optional[float]]] = []
    text_matrix: List[List[str]] = []
    hover_matrix: List[List[str]] = []

    for row in grid:
        z_row: List[Optional[float]] = []
        text_row: List[str] = []
        hover_row: List[str] = []
        for cell in row:
            if metric == "margin":
                val = float(cell.profit_margin_pct) if cell.profit_margin_pct is not None else None
                display_str = format_percentage(cell.profit_margin_pct)
            else:
                val = float(cell.profit)
                display_str = format_currency(cell.profit, currency)

            z_row.append(val if val is not None else 0.0)
            text_row.append(display_str)
            hover_row.append(
                f"Discount: {format_percentage(cell.discount_pct * Decimal('100'))}<br>"
                f"Labor Overrun: {format_percentage(cell.cost_overrun_pct * Decimal('100'))}<br>"
                f"Operating Profit: {format_currency(cell.profit, currency)}<br>"
                f"Profit Margin: {format_percentage(cell.profit_margin_pct)}<br>"
                f"Net Revenue: {format_currency(cell.net_revenue, currency)}"
            )
        z_values.append(z_row)
        text_matrix.append(text_row)
        hover_matrix.append(hover_row)

    colorscale = [
        [0.0, "#991B1B"],   # Dark red for heavy loss
        [0.25, "#EF4444"],  # Red for loss
        [0.45, "#F59E0B"],  # Amber for low margin
        [0.70, "#10B981"],  # Green for healthy margin
        [1.0, "#065F46"],   # Deep green for high margin
    ]

    metric_title = "Profit Margin (%)" if metric == "margin" else f"Operating Profit ({currency})"

    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=x_discounts,
            y=y_overruns,
            text=text_matrix,
            texttemplate="%{text}",
            textfont={"size": 11, "color": "#FFFFFF"},
            hovertext=hover_matrix,
            hoverinfo="text",
            colorscale=colorscale,
            colorbar=dict(title=metric_title, tickfont=dict(size=10, color="#475569")),
        )
    )

    fig.update_layout(
        title={
            "text": f"Sensitivity Matrix: {metric_title} under Cost Overrun vs. Client Discount",
            "font": {"size": 14, "color": "#1E293B"},
        },
        height=380,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(
            title="Client Discount (%)",
            tickfont=dict(size=11, color="#334155"),
            showgrid=False,
        ),
        yaxis=dict(
            title="Delivery Labor Cost Overrun (%)",
            tickfont=dict(size=11, color="#334155"),
            showgrid=False,
            autorange="reversed",
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
    )
    return fig


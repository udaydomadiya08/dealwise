"""DealWise - Consulting Proposal & Commercial Intelligence Platform.

Phases 1-4: Project Foundation, Commercial Engine, Executive Dashboard & Scenario Simulator.
"""

from decimal import Decimal
import streamlit as st
import plotly.graph_objects as go
from src.config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_VERSION,
    TARGET_ROLE,
    DISCLAIMER_TEXT,
    PAGES,
    get_navigation_map,
)
from src.commercial_engine import (
    CommercialInputs,
    CommercialResult,
    CommercialValidationError,
    calculate_commercials,
    format_currency,
    format_percentage,
)
from src.dashboard import (
    assess_commercial_health,
    build_revenue_vs_cost_chart,
    build_cost_composition_chart,
    build_profitability_benchmark_chart,
    build_sensitivity_heatmap,
    get_cost_composition,
)
from src.scenario_engine import (
    ScenarioComparison,
    SensitivityCell,
    compare_scenarios,
    generate_sensitivity_grid,
    evaluate_fixed_fee_model,
    evaluate_time_and_materials_model,
    export_scenario_to_csv,
)

# Page configuration
st.set_page_config(
    page_title=f"{APP_TITLE} | Commercial Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enterprise styling injection
st.markdown(
    """
    <style>
    /* Global styling overrides */
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header brand banner */
    .dw-header-card {
        background: linear-gradient(135deg, #0F2D59 0%, #1A467C 100%);
        color: #FFFFFF;
        padding: 22px 26px;
        border-radius: 10px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(15, 45, 89, 0.08);
    }
    .dw-header-card h1 {
        color: #FFFFFF !important;
        margin: 0;
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .dw-header-card p {
        color: #CBD5E1 !important;
        margin: 5px 0 0 0;
        font-size: 0.95rem;
    }
    
    /* Disclaimer banner */
    .dw-disclaimer-box {
        background-color: #EFF6FF;
        border-left: 4px solid #2563EB;
        padding: 10px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
        font-size: 0.85rem;
        color: #1E40AF;
        line-height: 1.45;
    }
    
    /* Metrics and cards */
    .dw-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .dw-card-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .dw-card-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.5px;
    }
    .dw-card-value-positive {
        color: #15803D !important;
    }
    .dw-card-value-negative {
        color: #DC2626 !important;
    }
    .dw-card-subtext {
        font-size: 0.80rem;
        color: #64748B;
        margin-top: 4px;
    }
    
    /* Pill badges */
    .dw-badge-active {
        background-color: #DCFCE7;
        color: #166534;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    .dw-badge-danger {
        background-color: #FEE2E2;
        color: #991B1B;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    .dw-badge-warning {
        background-color: #FEF3C7;
        color: #92400E;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    .dw-badge-upcoming {
        background-color: #F1F5F9;
        color: #475569;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    
    /* Health narrative card */
    .dw-health-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
        line-height: 1.55;
    }

    /* Clean sidebar aesthetic */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Synchronized session state defaults
DEFAULT_DEAL_PARAMS = {
    "base_quoted_price": 100000.0,
    "delivery_costs": 50000.0,
    "software_costs": 6000.0,
    "other_expenses": 4000.0,
    "contingency_pct": 10.0,
    "discount_pct": 5.0,
    "cost_overrun_pct": 0.0,
    "target_margin_pct": 25.0,
    "currency_selection": "USD ($)",
}


def init_session_state():
    """Initialize shared commercial parameters across pages."""
    for key, val in DEFAULT_DEAL_PARAMS.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_active_inputs() -> CommercialInputs:
    """Build CommercialInputs from current session state."""
    return CommercialInputs.from_percentages(
        base_quoted_price=st.session_state["base_quoted_price"],
        delivery_costs=st.session_state["delivery_costs"],
        software_tooling_costs=st.session_state["software_costs"],
        other_expenses=st.session_state["other_expenses"],
        contingency_pct=st.session_state["contingency_pct"],
        discount_pct=st.session_state["discount_pct"],
        cost_overrun_pct=st.session_state["cost_overrun_pct"],
        target_margin_pct=st.session_state["target_margin_pct"],
    )


def get_active_currency() -> str:
    """Return active currency code (USD or INR)."""
    sel = st.session_state.get("currency_selection", "USD ($)")
    return "INR" if "INR" in sel else "USD"


def render_sidebar():
    """Render consulting navigation and metadata sidebar."""
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding-bottom: 12px; border-bottom: 1px solid #E2E8F0; margin-bottom: 18px;">
                <div style="font-size: 1.25rem; font-weight: 800; color: #0F2D59; letter-spacing: -0.5px;">
                    💼 {APP_TITLE}
                </div>
                <div style="font-size: 0.78rem; color: #64748B; margin-top: 2px;">
                    {TARGET_ROLE}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("PLATFORM NAVIGATION")

        nav_options = [f"{p.icon} {p.label}" for p in PAGES]
        selected_label = st.radio(
            label="Select Module",
            options=nav_options,
            index=0,
            label_visibility="collapsed",
        )

        selected_index = nav_options.index(selected_label)
        selected_section = PAGES[selected_index]

        st.divider()

        st.caption("ACTIVE DEAL CONTROLS")
        curr_options = ["USD ($)", "INR (₹)"]
        curr_index = curr_options.index(st.session_state.get("currency_selection", "USD ($)"))
        st.session_state["currency_selection"] = st.selectbox(
            "Display Currency",
            options=curr_options,
            index=curr_index,
            help="Modifies display formatting only. Financial calculations remain currency-neutral.",
        )

        st.divider()

        st.caption("ENVIRONMENT & GOVERNANCE")
        st.markdown(
            f"""
            <div style="font-size: 0.82rem; color: #475569; line-height: 1.6;">
                <div><strong>Build:</strong> <code>{APP_VERSION}</code></div>
                <div><strong>Simulator:</strong> Phase 4 Active</div>
                <div><strong>Engine:</strong> Python Decimal (Exact)</div>
                <div><strong>Data Mode:</strong> Synthetic Only</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.caption("PORTFOLIO CONTEXT")
        st.markdown(
            """
            <div style="font-size: 0.78rem; color: #64748B; line-height: 1.45;">
                Engineered to demonstrate practical commercial architecture, pricing governance, what-if sensitivity modeling, and executive analytics for advisory engagements.
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_section


def render_header(section):
    """Render top brand header and transparency notice."""
    st.markdown(
        f"""
        <div class="dw-header-card">
            <h1>{APP_TITLE} — {APP_SUBTITLE}</h1>
            <p>Commercial Structuring • Deal Governance • What-If Scenario Intelligence</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="dw-disclaimer-box">
            <strong>NOTICE:</strong> {DISCLAIMER_TEXT}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview_page():
    """Render Phase 3 Executive Analytics Dashboard powered by the live commercial engine."""
    st.subheader("📊 Executive Commercial Dashboard")
    st.markdown(
        """
        High-level commercial intelligence briefing synthesized directly from the active calculation engine. 
        Evaluates engagement profitability, cost structure, break-even thresholds, and margin realization.
        """
    )

    currency = get_active_currency()

    try:
        inputs = get_active_inputs()
        res = calculate_commercials(inputs)
        health = assess_commercial_health(res, inputs.target_margin_pct)
        valid = True
    except CommercialValidationError as exc:
        st.error(f"⚠️ Calculation Error: {exc}. Please adjust values in the Commercial Analysis module.")
        valid = False

    if valid:
        # Context bar showing active baseline
        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 16px; margin-bottom: 16px; font-size: 0.84rem; color: #334155;">
                <strong>Active Proposal Parameters:</strong> Quoted Base: <strong>{format_currency(inputs.base_quoted_price, currency)}</strong> | 
                Client Discount: <strong>{format_percentage(inputs.discount_pct * Decimal('100'))}</strong> | 
                Delivery Costs: <strong>{format_currency(inputs.delivery_costs, currency)}</strong> | 
                Contingency: <strong>{format_percentage(inputs.contingency_pct * Decimal('100'))}</strong> | 
                Target Margin: <strong>{format_percentage(inputs.target_margin_pct * Decimal('100'))}</strong> | 
                Currency: <strong>{currency}</strong>
                <span style="color: #64748B; margin-left: 8px;">(Hypothetical Demonstration Values)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Row 1 of Executive KPIs
        k1, k2, k3 = st.columns(3)

        with k1:
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Net Realized Revenue</div>
                    <div class="dw-card-value">{format_currency(res.net_revenue, currency)}</div>
                    <div class="dw-card-subtext">Base {format_currency(inputs.base_quoted_price, currency)} minus {format_percentage(inputs.discount_pct * Decimal('100'))} discount</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k2:
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Estimated Total Cost</div>
                    <div class="dw-card-value">{format_currency(res.scenario_total_cost, currency)}</div>
                    <div class="dw-card-subtext">Direct ({format_currency(res.direct_estimated_cost, currency)}) + Contingency ({format_currency(res.contingency_amount, currency)})</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k3:
            profit_class = "dw-card-value-positive" if res.profit >= 0 else "dw-card-value-negative"
            profit_badge = '<span class="dw-badge-active">Profitable</span>' if res.profit > 0 else (
                '<span class="dw-badge-danger">Operating Loss</span>' if res.profit < 0 else '<span class="dw-badge-warning">Break-Even</span>'
            )
            profit_type_label = "Projected Operating Profit" if res.profit >= 0 else "Projected Operating Deficit"
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">{profit_type_label}</div>
                    <div class="dw-card-value {profit_class}">{format_currency(res.profit, currency)}</div>
                    <div class="dw-card-subtext">{profit_badge} Net Revenue - Scenario Cost</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Row 2 of Executive KPIs
        k4, k5, k6 = st.columns(3)

        with k4:
            margin_class = "dw-card-value-positive" if res.meets_target_margin else (
                "dw-card-value-negative" if (res.profit_margin_pct or Decimal("0")) < 0 else ""
            )
            margin_badge = '<span class="dw-badge-active">Target Met</span>' if res.meets_target_margin else (
                '<span class="dw-badge-warning">Below Target</span>' if res.is_profitable else '<span class="dw-badge-danger">Deficit</span>'
            )
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Projected Profit Margin</div>
                    <div class="dw-card-value {margin_class}">{format_percentage(res.profit_margin_pct)}</div>
                    <div class="dw-card-subtext">{margin_badge} Share of Net Revenue retained as profit</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k5:
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Target Practice Margin</div>
                    <div class="dw-card-value">{format_percentage(inputs.target_margin_pct * Decimal('100'))}</div>
                    <div class="dw-card-subtext">Practice governance benchmark threshold</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k6:
            be_surplus = health.break_even_difference
            be_class = "dw-card-value-positive" if be_surplus >= 0 else "dw-card-value-negative"
            be_text = f"+{format_currency(be_surplus, currency)} surplus" if be_surplus >= 0 else f"{format_currency(be_surplus, currency)} shortfall"
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Break-Even Revenue</div>
                    <div class="dw-card-value">{format_currency(res.break_even_net_revenue, currency)}</div>
                    <div class="dw-card-subtext <span class='{be_class}'><strong>{be_text}</strong> vs net revenue</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Commercial Health Assessment & Interpretation
        st.markdown("#### Commercial Health & Executive Interpretation")
        status_color = "#15803D" if health.meets_target_margin else ("#D97706" if health.is_profitable else "#DC2626")
        st.markdown(
            f"""
            <div class="dw-health-card" style="border-left: 5px solid {status_color};">
                <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; font-size: 0.95rem; color: #1E293B;">EXECUTIVE ADVISORY BRIEF:</span>
                    <span class="{'dw-badge-active' if health.is_profitable else 'dw-badge-danger'}">Status: {health.profitability_status}</span>
                    <span class="{'dw-badge-active' if health.meets_target_margin else 'dw-badge-warning'}">Margin: {health.margin_target_status}</span>
                </div>
                <div style="font-size: 0.90rem; color: #334155; margin-bottom: 10px;">
                    {health.executive_narrative}
                </div>
                <div style="font-size: 0.84rem; color: #64748B; border-top: 1px dashed #E2E8F0; padding-top: 8px;">
                    <strong>Economics Diagnostic:</strong> {health.margin_vs_markup_summary}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Executive Visualizations (Plotly)
        st.markdown("#### Commercial Structure & Benchmark Visualizations")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            fig_rev = build_revenue_vs_cost_chart(res, currency)
            st.plotly_chart(fig_rev, use_container_width=True)

        with chart_col2:
            fig_comp = build_cost_composition_chart(inputs, res, currency)
            st.plotly_chart(fig_comp, use_container_width=True)

        fig_bench = build_profitability_benchmark_chart(res, inputs.target_margin_pct)
        st.plotly_chart(fig_bench, use_container_width=True)

        st.caption(
            "Visualizations are generated directly from the underlying Decimal commercial engine. "
            "To model alternate fee structures, discounts, or delivery cost stress-tests, switch to the "
            "**Scenario Simulator** or **Commercial Analysis** module in the sidebar."
        )

    st.divider()

    # Value Design Pipeline Architecture (from Phase 1)
    st.markdown("#### 4-Stage Advisory Deal Lifecycle")
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.markdown(
            """
            <div class="dw-card">
                <div style="font-size: 1.05rem; font-weight: 700; color: #0F2D59;">1. Resource Scoping</div>
                <div style="font-size: 0.80rem; color: #64748B; margin-top: 4px;">
                    Define project duration, workstreams, and team pyramid ratios.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            """
            <div class="dw-card">
                <div style="font-size: 1.05rem; font-weight: 700; color: #0F2D59;">2. Commercial Structuring</div>
                <div style="font-size: 0.80rem; color: #64748B; margin-top: 4px;">
                    Compute direct cost baselines, standard rate realization, and margin.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p3:
        st.markdown(
            """
            <div class="dw-card">
                <div style="font-size: 1.05rem; font-weight: 700; color: #0F2D59;">3. Risk & Stress Testing</div>
                <div style="font-size: 0.80rem; color: #64748B; margin-top: 4px;">
                    Simulate scope creep, restaffing delays, and milestone slippage.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p4:
        st.markdown(
            """
            <div class="dw-card">
                <div style="font-size: 1.05rem; font-weight: 700; color: #0F2D59;">4. Governance & Audit</div>
                <div style="font-size: 0.80rem; color: #64748B; margin-top: 4px;">
                    Export partner commercial briefings and client fee schedules.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_commercial_analysis_page():
    """Render Phase 2 Commercial Analysis Interface with interactive engine."""
    st.subheader("💼 Commercial Deal Analysis & Margin Optimization")
    st.markdown(
        """
        Model proposed engagement financials, evaluate delivery cost components, stress-test cost overruns, 
        and calculate break-even and target-margin required fees with exact Decimal precision.
        """
    )

    currency = get_active_currency()

    st.markdown(
        f"""
        <div style="background-color: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 8px; padding: 10px 14px; font-size: 0.82rem; color: #475569; margin-bottom: 14px;">
            <strong>Hypothetical Demonstration Baseline:</strong> Parameters are synchronized with the Executive Dashboard. 
            Modifying any input updates all platform views immediately. Display Currency: <strong>{currency}</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    in_col1, in_col2 = st.columns(2)

    with in_col1:
        st.markdown("##### 1. Commercial Pricing & Terms")
        st.session_state["base_quoted_price"] = st.number_input(
            "Base Quoted Price",
            min_value=0.0,
            max_value=100000000.0,
            value=float(st.session_state["base_quoted_price"]),
            step=5000.0,
            help="Catalog or gross proposed fee before client discount.",
        )
        st.session_state["discount_pct"] = st.number_input(
            "Client Discount (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state["discount_pct"]),
            step=0.5,
            help="Negotiated commercial concession or rate reduction percentage.",
        )
        st.session_state["target_margin_pct"] = st.number_input(
            "Target Profit Margin (%)",
            min_value=0.0,
            max_value=99.99,
            value=float(st.session_state["target_margin_pct"]),
            step=1.0,
            help="Practice-mandated profit margin threshold (must be strictly below 100%).",
        )

    with in_col2:
        st.markdown("##### 2. Delivery Costs & Scenarios")
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            st.session_state["delivery_costs"] = st.number_input(
                "Delivery Costs (Labour & Subs)",
                min_value=0.0,
                max_value=100000000.0,
                value=float(st.session_state["delivery_costs"]),
                step=2500.0,
                help="Direct delivery personnel, consultants, and specialized subcontractors.",
            )
            st.session_state["software_costs"] = st.number_input(
                "Software & Cloud Tooling",
                min_value=0.0,
                max_value=10000000.0,
                value=float(st.session_state["software_costs"]),
                step=500.0,
                help="Engagement-specific cloud computing, SaaS licensing, and sandbox environments.",
            )
        with c_sub2:
            st.session_state["other_expenses"] = st.number_input(
                "Other Project Expenses",
                min_value=0.0,
                max_value=10000000.0,
                value=float(st.session_state["other_expenses"]),
                step=500.0,
                help="Travel, per diems, legal, compliance, and client-site materials.",
            )
            st.session_state["contingency_pct"] = st.number_input(
                "Contingency Reserve (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state["contingency_pct"]),
                step=1.0,
                help="Buffer applied to direct estimated cost to absorb standard delivery variance.",
            )

        st.session_state["cost_overrun_pct"] = st.number_input(
            "Delivery-Cost Overrun (%) [Stress Test]",
            min_value=0.0,
            max_value=200.0,
            value=float(st.session_state["cost_overrun_pct"]),
            step=5.0,
            help="Simulates percentage increase in labor/subcontractor costs due to scope or timeline elongation.",
        )

    try:
        inputs = get_active_inputs()
        res = calculate_commercials(inputs)
        valid = True
    except CommercialValidationError as exc:
        st.error(f"⚠️ Input Validation Error: {exc}")
        valid = False

    if valid:
        st.markdown("---")

        if res.profit < Decimal("0"):
            st.error(
                f"🚨 **CRITICAL COMMERCIAL RISK — NET OPERATING LOSS**: "
                f"The projected engagement results in a loss of **{format_currency(res.profit, currency)}** "
                f"(Profit Margin: {format_percentage(res.profit_margin_pct)}). "
                f"Break-even net revenue is **{format_currency(res.break_even_net_revenue, currency)}**."
            )
        elif not res.meets_target_margin:
            st.warning(
                f"⚠️ **TARGET MARGIN DEFICIT**: "
                f"Projected margin of **{format_percentage(res.profit_margin_pct)}** is below your practice target of **{format_percentage(inputs.target_margin_pct * Decimal('100'))}%** "
                f"(Deficit: {format_percentage(abs(res.margin_gap_pct) if res.margin_gap_pct is not None else 0)}). "
                f"To achieve target margin, required net price is **{format_currency(res.required_net_price, currency)}** "
                f"(or quote **{format_currency(res.required_quoted_price, currency)}** before discount)."
            )
        else:
            st.success(
                f"✅ **COMMERCIAL THRESHOLD MET**: "
                f"Projected margin of **{format_percentage(res.profit_margin_pct)}** satisfies the practice target of **{format_percentage(inputs.target_margin_pct * Decimal('100'))}%** "
                f"(Buffer: +{format_percentage(res.margin_gap_pct)})."
            )

        st.markdown("#### Deal Commercial Performance Indicators")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        with kpi1:
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Net Revenue</div>
                    <div class="dw-card-value">{format_currency(res.net_revenue, currency)}</div>
                    <div class="dw-card-subtext">After {format_percentage(inputs.discount_pct * Decimal('100'))} discount</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with kpi2:
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Scenario Total Cost</div>
                    <div class="dw-card-value">{format_currency(res.scenario_total_cost, currency)}</div>
                    <div class="dw-card-subtext">Direct + Contingency + Overrun</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with kpi3:
            profit_class = "dw-card-value-positive" if res.profit >= 0 else "dw-card-value-negative"
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Projected Profit</div>
                    <div class="dw-card-value {profit_class}">{format_currency(res.profit, currency)}</div>
                    <div class="dw-card-subtext">Net Revenue - Scenario Cost</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with kpi4:
            margin_class = "dw-card-value-positive" if res.meets_target_margin else ("dw-card-value-negative" if (res.profit_margin_pct or 0) < 0 else "")
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Profit Margin</div>
                    <div class="dw-card-value {margin_class}">{format_percentage(res.profit_margin_pct)}</div>
                    <div class="dw-card-subtext">Target: {format_percentage(inputs.target_margin_pct * Decimal('100'))}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        skpi1, skpi2, skpi3, skpi4 = st.columns(4)

        with skpi1:
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Markup on Cost</div>
                    <div class="dw-card-value">{format_percentage(res.markup_pct)}</div>
                    <div class="dw-card-subtext">Profit ÷ Total Cost (Cost Denominator)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with skpi2:
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Break-Even Net Revenue</div>
                    <div class="dw-card-value">{format_currency(res.break_even_net_revenue, currency)}</div>
                    <div class="dw-card-subtext">Zero-profit revenue threshold</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with skpi3:
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Target Net Price</div>
                    <div class="dw-card-value">{format_currency(res.required_net_price, currency)}</div>
                    <div class="dw-card-subtext">Net fee needed for {format_percentage(inputs.target_margin_pct * Decimal('100'))}% margin</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with skpi4:
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Target Quoted Price</div>
                    <div class="dw-card-value">{format_currency(res.required_quoted_price, currency)}</div>
                    <div class="dw-card-subtext">Quote before {format_percentage(inputs.discount_pct * Decimal('100'))} discount</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### Cost Architecture & Breakdown")
        cost_col, summary_col = st.columns([3, 2])

        with cost_col:
            breakdown_data = {
                "Cost Category": [
                    "Direct Delivery Labor & Subcontractors",
                    "Software, Cloud & Tooling",
                    "Other Project Expenses",
                    "Direct Estimated Cost (Subtotal)",
                    "Contingency Reserve Amount",
                    "Baseline Total Estimated Cost",
                    "Delivery-Cost Overrun Impact",
                    "Scenario Total Estimated Cost",
                ],
                "Basis / Formula": [
                    "Quoted labor allocation",
                    "Fixed engagement software/cloud",
                    "Expenses & travel",
                    "Delivery + Software + Expenses",
                    f"{format_percentage(inputs.contingency_pct * Decimal('100'))} of Direct Estimated Cost",
                    "Direct Cost + Contingency",
                    f"{format_percentage(inputs.cost_overrun_pct * Decimal('100'))} overrun on Delivery Costs",
                    "Scenario Delivery + Software + Expenses + Contingency",
                ],
                f"Amount ({currency})": [
                    format_currency(inputs.delivery_costs, currency),
                    format_currency(inputs.software_tooling_costs, currency),
                    format_currency(inputs.other_expenses, currency),
                    format_currency(res.direct_estimated_cost, currency),
                    format_currency(res.contingency_amount, currency),
                    format_currency(res.baseline_total_cost, currency),
                    format_currency(res.scenario_delivery_cost - inputs.delivery_costs, currency),
                    format_currency(res.scenario_total_cost, currency),
                ],
            }
            st.table(breakdown_data)

        with summary_col:
            fig_comp = build_cost_composition_chart(inputs, res, currency)
            st.plotly_chart(fig_comp, use_container_width=True)


def render_scenario_simulator_page():
    """Render Phase 4 What-If Scenario Simulator, Sensitivity Grid, and Contract Models."""
    st.subheader("🎛️ What-If Commercial Scenario Simulator")
    st.markdown(
        """
        Evaluate proposed client concessions, labor delivery stress-tests, sensitivity surfaces, 
        and commercial contract structures side-by-side with your saved baseline.
        """
    )

    currency = get_active_currency()
    baseline_inputs = get_active_inputs()

    # Preset selection bar
    st.markdown("##### 1. Define What-If Scenario")
    preset_col, info_col = st.columns([1, 2])

    with preset_col:
        preset_name = st.selectbox(
            "Scenario Preset",
            options=[
                "Custom Scenario",
                "Aggressive Negotiation (15% Client Discount)",
                "Delivery Labor Overrun (+20% Scope Creep)",
                "Compound Downside (15% Discount + 25% Overrun)",
                "Optimized Execution (0% Overrun & 0% Discount)",
            ],
            index=0,
            help="Choose a pre-configured commercial situation or adjust parameters manually.",
        )

    # Preset default overrides for scenario inputs
    def_price = float(baseline_inputs.base_quoted_price)
    def_disc = float(baseline_inputs.discount_pct * Decimal("100"))
    def_overrun = float(baseline_inputs.cost_overrun_pct * Decimal("100"))
    def_cont = float(baseline_inputs.contingency_pct * Decimal("100"))

    if preset_name == "Aggressive Negotiation (15% Client Discount)":
        def_disc = 15.0
    elif preset_name == "Delivery Labor Overrun (+20% Scope Creep)":
        def_overrun = 20.0
    elif preset_name == "Compound Downside (15% Discount + 25% Overrun)":
        def_disc = 15.0
        def_overrun = 25.0
    elif preset_name == "Optimized Execution (0% Overrun & 0% Discount)":
        def_disc = 0.0
        def_overrun = 0.0

    with info_col:
        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px 16px; margin-top: 12px; font-size: 0.83rem; color: #334155;">
                <strong>Baseline Protected:</strong> The saved deal baseline (Quoted: {format_currency(baseline_inputs.base_quoted_price, currency)}, 
                Discount: {format_percentage(baseline_inputs.discount_pct * Decimal('100'))}, Delivery: {format_currency(baseline_inputs.delivery_costs, currency)}) 
                remains unmutated while running what-if simulations.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Scenario Controls Layout
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)

    with s_col1:
        scen_price = st.number_input(
            "Scenario Quoted Price",
            min_value=0.0,
            max_value=100000000.0,
            value=def_price,
            step=5000.0,
            help="Simulated gross catalog fee.",
        )

    with s_col2:
        scen_discount = st.number_input(
            "Scenario Client Discount (%)",
            min_value=0.0,
            max_value=100.0,
            value=def_disc,
            step=1.0,
            help="Simulated negotiated discount concession.",
        )

    with s_col3:
        scen_overrun = st.number_input(
            "Scenario Labor Overrun (%)",
            min_value=0.0,
            max_value=300.0,
            value=def_overrun,
            step=5.0,
            help="Simulated labor cost overrun on delivery personnel.",
        )

    with s_col4:
        scen_contingency = st.number_input(
            "Scenario Contingency (%)",
            min_value=0.0,
            max_value=100.0,
            value=def_cont,
            step=1.0,
            help="Simulated contingency reserve rate.",
        )

    # Build and validate scenario inputs
    try:
        scenario_inputs = CommercialInputs.from_percentages(
            base_quoted_price=scen_price,
            delivery_costs=baseline_inputs.delivery_costs,
            software_tooling_costs=baseline_inputs.software_tooling_costs,
            other_expenses=baseline_inputs.other_expenses,
            contingency_pct=scen_contingency,
            discount_pct=scen_discount,
            cost_overrun_pct=scen_overrun,
            target_margin_pct=baseline_inputs.target_margin_pct * Decimal("100"),
        )
        comparison = compare_scenarios(baseline_inputs, scenario_inputs)
        valid_scenario = True
    except CommercialValidationError as exc:
        st.error(f"⚠️ Scenario Input Error: {exc}")
        valid_scenario = False

    if valid_scenario:
        st.markdown("---")
        st.markdown("##### 2. Baseline vs. Scenario Comparative Delta")

        # 4 Delta KPI Cards
        d1, d2, d3, d4 = st.columns(4)

        with d1:
            delta_rev = comparison.delta_net_revenue
            rev_color = "dw-card-value-positive" if delta_rev >= 0 else "dw-card-value-negative"
            rev_sign = "+" if delta_rev >= 0 else ""
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Net Revenue Impact</div>
                    <div class="dw-card-value {rev_color}">{rev_sign}{format_currency(delta_rev, currency)}</div>
                    <div class="dw-card-subtext">Scenario: {format_currency(comparison.scenario_result.net_revenue, currency)} vs Base: {format_currency(comparison.baseline_result.net_revenue, currency)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with d2:
            delta_cost = comparison.delta_total_cost
            cost_color = "dw-card-value-negative" if delta_cost > 0 else ("dw-card-value-positive" if delta_cost < 0 else "")
            cost_sign = "+" if delta_cost >= 0 else ""
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Total Cost Impact</div>
                    <div class="dw-card-value {cost_color}">{cost_sign}{format_currency(delta_cost, currency)}</div>
                    <div class="dw-card-subtext">Scenario: {format_currency(comparison.scenario_result.scenario_total_cost, currency)} vs Base: {format_currency(comparison.baseline_result.scenario_total_cost, currency)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with d3:
            delta_prof = comparison.delta_profit
            prof_color = "dw-card-value-positive" if delta_prof >= 0 else "dw-card-value-negative"
            prof_sign = "+" if delta_prof >= 0 else ""
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Profit Impact</div>
                    <div class="dw-card-value {prof_color}">{prof_sign}{format_currency(delta_prof, currency)}</div>
                    <div class="dw-card-subtext">Scenario: {format_currency(comparison.scenario_result.profit, currency)} vs Base: {format_currency(comparison.baseline_result.profit, currency)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with d4:
            delta_m = comparison.delta_margin_percentage_points
            margin_color = "dw-card-value-positive" if (delta_m or 0) >= 0 else "dw-card-value-negative"
            margin_sign = "+" if (delta_m or 0) >= 0 else ""
            delta_m_str = f"{margin_sign}{delta_m:.2f} pp" if delta_m is not None else "N/A"
            scen_m_str = format_percentage(comparison.scenario_result.profit_margin_pct)
            base_m_str = format_percentage(comparison.baseline_result.profit_margin_pct)
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Margin Variance (pp)</div>
                    <div class="dw-card-value {margin_color}">{delta_m_str}</div>
                    <div class="dw-card-subtext">Scenario: {scen_m_str} vs Base: {base_m_str}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Tabular Side-by-Side Comparison
        comp_table_data = {
            "Metric": [
                "Net Realized Revenue",
                "Direct Estimated Cost",
                "Contingency Reserve Amount",
                "Scenario Total Estimated Cost",
                "Projected Operating Profit / Loss",
                "Profit Margin (%)",
                "Markup on Cost (%)",
                "Target Practice Margin (%)",
                "Target Margin Achieved?",
            ],
            "Saved Baseline": [
                format_currency(comparison.baseline_result.net_revenue, currency),
                format_currency(comparison.baseline_result.direct_estimated_cost, currency),
                format_currency(comparison.baseline_result.contingency_amount, currency),
                format_currency(comparison.baseline_result.scenario_total_cost, currency),
                format_currency(comparison.baseline_result.profit, currency),
                format_percentage(comparison.baseline_result.profit_margin_pct),
                format_percentage(comparison.baseline_result.markup_pct),
                format_percentage(baseline_inputs.target_margin_pct * Decimal("100")),
                "YES" if comparison.baseline_result.meets_target_margin else "NO",
            ],
            "What-If Scenario": [
                format_currency(comparison.scenario_result.net_revenue, currency),
                format_currency(comparison.scenario_result.direct_estimated_cost, currency),
                format_currency(comparison.scenario_result.contingency_amount, currency),
                format_currency(comparison.scenario_result.scenario_total_cost, currency),
                format_currency(comparison.scenario_result.profit, currency),
                format_percentage(comparison.scenario_result.profit_margin_pct),
                format_percentage(comparison.scenario_result.markup_pct),
                format_percentage(baseline_inputs.target_margin_pct * Decimal("100")),
                "YES" if comparison.scenario_result.meets_target_margin else "NO",
            ],
            "Variance (Delta)": [
                format_currency(comparison.delta_net_revenue, currency),
                format_currency(comparison.scenario_result.direct_estimated_cost - comparison.baseline_result.direct_estimated_cost, currency),
                format_currency(comparison.scenario_result.contingency_amount - comparison.baseline_result.contingency_amount, currency),
                format_currency(comparison.delta_total_cost, currency),
                format_currency(comparison.delta_profit, currency),
                f"{comparison.delta_margin_percentage_points:+.2f} pp" if comparison.delta_margin_percentage_points is not None else "N/A",
                f"{comparison.delta_markup_percentage_points:+.2f} pp" if comparison.delta_markup_percentage_points is not None else "N/A",
                "—",
                "Improvement" if comparison.scenario_result.meets_target_margin and not comparison.baseline_result.meets_target_margin else (
                    "Deterioration" if not comparison.scenario_result.meets_target_margin and comparison.baseline_result.meets_target_margin else "Unchanged"
                ),
            ],
        }
        st.table(comp_table_data)

        st.markdown("---")

        # 3. Sensitivity Analysis Heatmap
        st.markdown("##### 3. Sensitivity Analysis Matrix")
        st.markdown(
            """
            Evaluate how varying client discounts and labor cost overruns simultaneously alter engagement economics. 
            Every cell is calculated dynamically through the commercial engine.
            """
        )

        h_col1, h_col2 = st.columns([1, 3])
        with h_col1:
            heatmap_metric = st.selectbox(
                "Sensitivity Metric",
                options=["Profit Margin (%)", "Operating Profit"],
                index=0,
                help="Select whether cells display percentage profit margin or absolute operating profit.",
            )
            metric_key = "margin" if "Margin" in heatmap_metric else "profit"

        with h_col2:
            st.caption(
                "ℹ️ **Methodology Notice:** This matrix represents a deterministic sensitivity analysis across static assumptions, "
                "not an empirical statistical forecast or Monte Carlo probability distribution."
            )

        # Generate standard sensitivity grid (0-20% discount, 0-25% overrun)
        sensitivity_grid = generate_sensitivity_grid(
            base_inputs=scenario_inputs,
            discount_steps=["0.0", "5.0", "10.0", "15.0", "20.0"],
            overrun_steps=["0.0", "5.0", "10.0", "15.0", "20.0", "25.0"],
            rates_as_percentages=True,
        )

        fig_heat = build_sensitivity_heatmap(sensitivity_grid, currency, metric=metric_key)
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("---")

        # 4. Contracting Commercial Models Comparison (Fixed Fee vs. T&M)
        st.markdown("##### 4. Contracting Structure Trade-Off: Fixed Fee vs. Time & Materials")
        st.markdown(
            """
            Different contracting arrangements allocate delivery variance risk between the client and the consulting firm. 
            Below is an illustrative comparison of economic outcomes under equal baseline delivery scope.
            """
        )

        m_col1, m_col2 = st.columns(2)

        with m_col1:
            st.markdown("###### Fixed Fee Contract Model")
            ff_fee = st.number_input(
                "Agreed Fixed Contract Price",
                min_value=0.0,
                value=float(scen_price),
                step=5000.0,
                key="ff_fee",
            )
            ff_overrun = st.number_input(
                "Fixed Fee Labor Overrun (%)",
                min_value=0.0,
                max_value=200.0,
                value=float(scen_overrun),
                step=5.0,
                key="ff_overrun",
            )

            ff_eval = evaluate_fixed_fee_model(
                agreed_fixed_fee=ff_fee,
                delivery_costs=baseline_inputs.delivery_costs,
                software_and_expenses=baseline_inputs.software_tooling_costs + baseline_inputs.other_expenses,
                contingency_pct=scen_contingency,
                cost_overrun_pct=ff_overrun,
            )

            st.markdown(
                f"""
                <div class="dw-card">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #0F2D59;">Fixed Fee Economic Outcome</div>
                    <div style="font-size: 0.84rem; margin-top: 6px; line-height: 1.6; color: #334155;">
                        <div><strong>Revenue:</strong> {format_currency(ff_eval.revenue, currency)} (Locked)</div>
                        <div><strong>Total Delivery Cost:</strong> {format_currency(ff_eval.total_cost, currency)}</div>
                        <div><strong>Operating Profit:</strong> {format_currency(ff_eval.profit, currency)}</div>
                        <div><strong>Profit Margin:</strong> {format_percentage(ff_eval.profit_margin_pct)}</div>
                    </div>
                    <div style="font-size: 0.78rem; color: #991B1B; margin-top: 8px; border-top: 1px dashed #CBD5E1; padding-top: 6px;">
                        <strong>Risk Allocation:</strong> {ff_eval.risk_allocation}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with m_col2:
            st.markdown("###### Time & Materials (T&M) Model")
            tm_hours = st.number_input(
                "Planned Billable Hours",
                min_value=1.0,
                value=500.0,
                step=50.0,
                key="tm_hours",
            )
            tm_rate_col1, tm_rate_col2 = st.columns(2)
            with tm_rate_col1:
                tm_bill_rate = st.number_input(
                    "Billing Rate / hr",
                    min_value=0.0,
                    value=200.0,
                    step=10.0,
                    key="tm_bill",
                )
            with tm_rate_col2:
                tm_cost_rate = st.number_input(
                    "Cost Rate / hr",
                    min_value=0.0,
                    value=100.0,
                    step=10.0,
                    key="tm_cost",
                )

            tm_hours_overrun = st.number_input(
                "Hours Overrun (%)",
                min_value=0.0,
                max_value=200.0,
                value=float(scen_overrun),
                step=5.0,
                key="tm_overrun",
            )

            tm_eval = evaluate_time_and_materials_model(
                billable_hours=tm_hours,
                billing_rate_per_hour=tm_bill_rate,
                cost_rate_per_hour=tm_cost_rate,
                software_and_expenses=baseline_inputs.software_tooling_costs + baseline_inputs.other_expenses,
                contingency_pct=0.0,
                hours_overrun_pct=tm_hours_overrun,
            )

            st.markdown(
                f"""
                <div class="dw-card">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #0F2D59;">Time & Materials Outcome</div>
                    <div style="font-size: 0.84rem; margin-top: 6px; line-height: 1.6; color: #334155;">
                        <div><strong>Revenue:</strong> {format_currency(tm_eval.revenue, currency)} (Billed for hours)</div>
                        <div><strong>Total Delivery Cost:</strong> {format_currency(tm_eval.total_cost, currency)}</div>
                        <div><strong>Operating Profit:</strong> {format_currency(tm_eval.profit, currency)}</div>
                        <div><strong>Profit Margin:</strong> {format_percentage(tm_eval.profit_margin_pct)}</div>
                    </div>
                    <div style="font-size: 0.78rem; color: #15803D; margin-top: 8px; border-top: 1px dashed #CBD5E1; padding-top: 6px;">
                        <strong>Risk Allocation:</strong> {tm_eval.risk_allocation}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # 5. Export Scenario & Sensitivity Results to CSV
        st.markdown("##### 5. Export Scenario Analysis to Spreadsheet (CSV)")
        st.markdown(
            "Download a complete audit package containing baseline parameters, scenario deltas, and sensitivity grid data."
        )

        csv_content = export_scenario_to_csv(
            comparison=comparison,
            sensitivity_grid=sensitivity_grid,
            currency_code=currency,
        )

        st.download_button(
            label="📥 Download Scenario & Sensitivity Audit (CSV)",
            data=csv_content,
            file_name="dealwise_scenario_simulation.csv",
            mime="text/csv",
            help="Exports complete numeric model data for Excel or spreadsheet analysis.",
        )


def render_planned_section_view(section):
    """Render planned module placeholder with architecture and requirements blueprint."""
    st.subheader(f"{section.icon} {section.label}")
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <span class="dw-badge-upcoming">Target Release: Phase {section.phase}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(f"**Module Objective**: {section.summary}")

    st.markdown("#### Planned Architectural Components")

    if section.key == "risk_review":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                """
                **Risk Drivers to Model**:
                - Scope volatility and unplanned rework cycles
                - Ramp-up staffing lag and onboarding friction
                - Client dependency and data access delays
                - Senior SME bandwidth constraints
                """
            )
        with col2:
            st.markdown(
                """
                **Governance Metrics (Roadmap)**:
                - Recommended contingency buffer ($ and % of fee)
                - Break-even delivery duration threshold
                - Margin at Risk (MaR) calculation
                """
            )

    elif section.key == "proposal_reports":
        st.markdown(
            """
            **Deliverables Planned for Phase 5**:
            - **Executive Briefing Sheet**: One-page commercial summary designed for practice leader sign-off.
            - **Client Fee Schedule**: Transparent, professional pricing schedule suitable for proposal appendices.
            - **Governance Audit Log**: Version-controlled snapshot of pricing assumptions, approvals, and margin targets.
            """
        )

    st.warning(
        f"⚙️ **Status**: Module planned for upcoming implementation milestone (Phase {section.phase})."
    )


def main():
    init_session_state()
    selected_section = render_sidebar()
    render_header(selected_section)

    if selected_section.key == "overview":
        render_overview_page()
    elif selected_section.key == "commercial_analysis":
        render_commercial_analysis_page()
    elif selected_section.key == "scenario_simulator":
        render_scenario_simulator_page()
    else:
        render_planned_section_view(selected_section)


if __name__ == "__main__":
    main()

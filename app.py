"""DealWise - Consulting Proposal & Commercial Intelligence Platform.

Phases 1, 2 & 3: Project Foundation, Commercial Calculation Engine & Executive Analytics Dashboard.
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
    get_cost_composition,
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
    """Initialize shared commercial parameters across Overview and Analysis pages."""
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
                <div><strong>Dashboard:</strong> Phase 3 Active</div>
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
                Engineered to demonstrate practical commercial architecture, pricing governance, and executive analytics for advisory engagements.
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
            <p>Commercial Structuring • Deal Governance • Executive Proposal Analytics</p>
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

    # Calculate current commercial results
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

        # Benchmark Chart
        fig_bench = build_profitability_benchmark_chart(res, inputs.target_margin_pct)
        st.plotly_chart(fig_bench, use_container_width=True)

        st.caption(
            "Visualizations are generated directly from the underlying Decimal commercial engine. "
            "To model alternate fee structures, discounts, or delivery cost stress-tests, switch to the "
            "**Commercial Analysis** module in the sidebar."
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

    # Notification banner
    st.markdown(
        f"""
        <div style="background-color: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 8px; padding: 10px 14px; font-size: 0.82rem; color: #475569; margin-bottom: 14px;">
            <strong>Hypothetical Demonstration Baseline:</strong> Parameters are synchronized with the Executive Dashboard. 
            Modifying any input updates both views immediately. Display Currency: <strong>{currency}</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Inputs Layout (2 columns: Commercial Pricing vs Delivery Costs)
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

    # Calculation execution with robust error handling
    try:
        inputs = get_active_inputs()
        res = calculate_commercials(inputs)
        valid = True
    except CommercialValidationError as exc:
        st.error(f"⚠️ Input Validation Error: {exc}")
        valid = False

    if valid:
        st.markdown("---")

        # Commercial Health Warnings & Alerts
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

        # Primary Executive KPIs
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

        # Secondary Advisory KPIs
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

        # Cost Component Breakdown & Structure
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

        # Transparent Formula Reference
        with st.expander("📐 Transparent Financial Engineering Reference (Formulas & Definitions)", expanded=False):
            st.markdown(
                """
                The DealWise calculation engine applies exact advisory deal economics:

                1. **Direct estimated cost** = $\\text{Delivery Costs} + \\text{Software/Tooling Costs} + \\text{Other Expenses}$
                2. **Contingency amount** = $\\text{Direct Estimated Cost} \\times \\text{Contingency \\%}$
                3. **Baseline total estimated cost** = $\\text{Direct Estimated Cost} + \\text{Contingency Amount}$
                4. **Scenario delivery cost** = $\\text{Delivery Costs} \\times (1 + \\text{Cost Overrun \\%})$
                5. **Scenario total estimated cost** = $\\text{Scenario Delivery Cost} + \\text{Software Costs} + \\text{Other Expenses} + \\text{Contingency Amount}$
                6. **Net revenue** = $\\text{Base Quoted Price} \\times (1 - \\text{Discount \\%})$
                7. **Profit** = $\\text{Net Revenue} - \\text{Scenario Total Estimated Cost}$
                8. **Profit margin (\\%)** = $\\frac{\\text{Profit}}{\\text{Net Revenue}} \\times 100$ *(when Net Revenue > 0)*
                9. **Markup (\\%)** = $\\frac{\\text{Profit}}{\\text{Scenario Total Estimated Cost}} \\times 100$ *(when Total Cost > 0)*
                10. **Break-even net revenue** = $\\text{Scenario Total Estimated Cost}$
                11. **Required net price for target margin** = $\\frac{\\text{Scenario Total Estimated Cost}}{1 - \\text{Target Margin \\%}}$ *(where Target Margin < 100\\%)*
                12. **Required quoted price before discount** = $\\frac{\\text{Required Net Price}}{1 - \\text{Discount \\%}}$ *(where Discount < 100\\%)*

                **Margin vs. Markup Distinction**:
                - **Profit Margin** uses **Revenue** as denominator: indicates the share of client fees retained as profit.
                - **Markup** uses **Cost** as denominator: indicates the percentage added on top of delivery costs.
                """
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

    if section.key == "scenario_simulator":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                """
                **Contract Structure Comparison**:
                - **Time & Materials (T&M)**: Low delivery risk, fee strictly tied to hours delivered.
                - **Capped T&M**: Shared risk model with not-to-exceed ceiling.
                - **Fixed Fee**: Full delivery commitment requiring explicit contingency reserve.
                - **Value-Linked Hybrid**: Reduced base fee with performance bonus upon KPI milestone sign-off.
                """
            )
        with col2:
            st.markdown(
                """
                **Interactive Controls (Roadmap)**:
                - Multi-deal comparison side-by-side matrices.
                - Sensitivity surface displaying margin variance across simultaneous rate and volume variations.
                """
            )

    elif section.key == "risk_review":
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
            **Deliverables Planned for Phase 4**:
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
    else:
        render_planned_section_view(selected_section)


if __name__ == "__main__":
    main()

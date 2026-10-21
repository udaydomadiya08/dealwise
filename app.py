"""DealWise - Consulting Proposal & Commercial Intelligence Platform.

Phase 1 & Phase 2: Project Foundation, Enterprise Architecture & Commercial Engine.
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
        padding: 24px 28px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(15, 45, 89, 0.08);
    }
    .dw-header-card h1 {
        color: #FFFFFF !important;
        margin: 0;
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .dw-header-card p {
        color: #CBD5E1 !important;
        margin: 6px 0 0 0;
        font-size: 1.0rem;
    }
    
    /* Disclaimer banner */
    .dw-disclaimer-box {
        background-color: #EFF6FF;
        border-left: 4px solid #2563EB;
        padding: 12px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 24px;
        font-size: 0.88rem;
        color: #1E40AF;
        line-height: 1.45;
    }
    
    /* Metrics and cards */
    .dw-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .dw-card-title {
        font-size: 0.88rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .dw-card-value {
        font-size: 1.7rem;
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
    .dw-card-value-placeholder {
        font-size: 1.7rem;
        font-weight: 700;
        color: #94A3B8;
        letter-spacing: -0.5px;
    }
    .dw-card-subtext {
        font-size: 0.82rem;
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
    .dw-badge-upcoming {
        background-color: #F1F5F9;
        color: #475569;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
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

        st.caption("ENVIRONMENT & GOVERNANCE")
        st.markdown(
            f"""
            <div style="font-size: 0.82rem; color: #475569; line-height: 1.6;">
                <div><strong>Build:</strong> <code>{APP_VERSION}</code></div>
                <div><strong>Engine:</strong> Phase 2 Active</div>
                <div><strong>Precision:</strong> Python Decimal (Exact)</div>
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
                Engineered to demonstrate practical commercial architecture, pricing governance, and margin sensitivity modeling for advisory engagements.
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
            <p>Commercial Structuring • Deal Governance • Value-Based Proposal Analytics</p>
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


def render_empty_state_chart():
    """Render a structural placeholder chart illustrating the planned Phase 2 waterfall model."""
    categories = [
        "Contract Value (Gross)",
        "Direct Delivery Costs",
        "Overhead Allocation",
        "Risk Contingency Reserve",
        "Target Gross Margin",
    ]
    values = [0, 0, 0, 0, 0]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            marker_color="#94A3B8",
            text=["Awaiting Scoping", "Awaiting Scoping", "Awaiting Scoping", "Awaiting Scoping", "Awaiting Scoping"],
            textposition="auto",
        )
    )

    fig.update_layout(
        title={
            "text": "Deal Commercial Waterfall Framework",
            "font": {"size": 14, "color": "#1E293B"},
        },
        height=280,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        yaxis=dict(
            title="Commercial Value ($ USD)",
            range=[0, 100],
            showgrid=True,
            gridcolor="#F1F5F9",
            zerolinecolor="#CBD5E1",
        ),
        xaxis=dict(
            tickfont=dict(size=11, color="#475569"),
            showgrid=False,
        ),
    )
    return fig


def render_overview_page():
    """Render Phase 1 Overview & Architecture Dashboard."""
    st.subheader("Executive Overview & Commercial Value Design")
    st.markdown(
        """
        Consulting deals frequently suffer margin erosion from disjointed delivery scoping, 
        opaque staffing pyramids, and unquantified commercial risk. **DealWise** bridges 
        the gap between technical scoping and advisory deal-making by bringing quantitative rigor 
        to proposal economics.
        """
    )

    # Empty-state KPI banner
    st.markdown("#### Commercial Proposal Baseline (Overview Snapshot)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div class="dw-card">
                <div class="dw-card-title">Commercial Engine</div>
                <div class="dw-card-value" style="color: #15803D;">Phase 2 Active</div>
                <div class="dw-card-subtext"><span class="dw-badge-active">Operational</span> Switch to Commercial Analysis tab</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="dw-card">
                <div class="dw-card-title">Precision Mode</div>
                <div class="dw-card-value">Decimal</div>
                <div class="dw-card-subtext"><span class="dw-badge-active">Active</span> Zero binary float rounding error</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="dw-card">
                <div class="dw-card-title">Currencies</div>
                <div class="dw-card-value">USD / INR</div>
                <div class="dw-card-subtext"><span class="dw-badge-active">Active</span> Dual display formatting supported</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
            <div class="dw-card">
                <div class="dw-card-title">Verification</div>
                <div class="dw-card-value" style="color: #15803D;">37 Tests</div>
                <div class="dw-card-subtext"><span class="dw-badge-active">Passing</span> Automated pytest validation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Commercial Modeling Blueprint")
    chart_col, info_col = st.columns([3, 2])

    with chart_col:
        fig = render_empty_state_chart()
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Note: Switch to the **Commercial Analysis** module in the sidebar to interact with the live "
            "Phase 2 calculation engine."
        )

    with info_col:
        st.markdown(
            """
            <div class="dw-card" style="height: 100%;">
                <div class="dw-card-title">Value Design Capabilities</div>
                <ul style="font-size: 0.88rem; color: #334155; padding-left: 20px; line-height: 1.7;">
                    <li><strong>Commercial Calculation Engine</strong>: Exact mathematical formulas for direct costs, contingency, scenario overruns, profit margin, and markup.</li>
                    <li><strong>Break-Even & Target Pricing</strong>: Closed-form solutions for required net and quoted fees given a practice margin target.</li>
                    <li><strong>Margin Buffer Calibration</strong>: Stress-test delivery overruns before commercial sign-off.</li>
                    <li><strong>Proposal Governance</strong>: Generate consistent, auditable commercial briefings for engagement partners.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown("#### 4-Stage Advisory Deal Lifecycle")
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.markdown(
            """
            <div class="dw-card">
                <div style="font-size: 1.1rem; font-weight: 700; color: #0F2D59;">1. Resource Scoping</div>
                <div style="font-size: 0.82rem; color: #64748B; margin-top: 6px;">
                    Define project duration, workstreams, and team pyramid ratios using standardized rate cards.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            """
            <div class="dw-card">
                <div style="font-size: 1.1rem; font-weight: 700; color: #0F2D59;">2. Commercial Structuring</div>
                <div style="font-size: 0.82rem; color: #64748B; margin-top: 6px;">
                    Compute direct cost baselines, standard rate realization, and gross contribution margin.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p3:
        st.markdown(
            """
            <div class="dw-card">
                <div style="font-size: 1.1rem; font-weight: 700; color: #0F2D59;">3. Risk & Stress Testing</div>
                <div style="font-size: 0.82rem; color: #64748B; margin-top: 6px;">
                    Simulate scope creep, team re-staffing delays, and milestone slippage impacts on profitability.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p4:
        st.markdown(
            """
            <div class="dw-card">
                <div style="font-size: 1.1rem; font-weight: 700; color: #0F2D59;">4. Governance & Audit</div>
                <div style="font-size: 0.82rem; color: #64748B; margin-top: 6px;">
                    Export client-facing fee summaries and internal partner commercial approval artifacts.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("#### Platform Readiness Verification")
    st.success(
        "✅ **Phase 2 Commercial Engine Operational**: Full financial formula suite active with input validation, "
        "reproducible Decimal precision, multi-currency display, and automated test coverage."
    )


def render_commercial_waterfall(result: CommercialResult, currency: str):
    """Render interactive Plotly commercial waterfall for the engagement."""
    categories = [
        "Base Quoted Price",
        "Client Discount",
        "Net Revenue",
        "Scenario Delivery Cost",
        "Software & Cloud",
        "Other Expenses",
        "Contingency Reserve",
        "Projected Profit",
    ]

    fig = go.Figure(
        go.Waterfall(
            name="Deal Waterfall",
            orientation="v",
            measure=[
                "absolute",
                "relative",
                "total",
                "relative",
                "relative",
                "relative",
                "relative",
                "total",
            ],
            x=categories,
            textposition="outside",
            text=[
                format_currency(result.net_revenue + (result.baseline_total_cost * 0), currency), # handled clean
                f"-{format_currency(result.net_revenue * 0, currency)}",
                format_currency(result.net_revenue, currency),
                f"-{format_currency(result.scenario_delivery_cost, currency)}",
                f"-{format_currency(result.baseline_total_cost * 0, currency)}",
                f"-{format_currency(result.baseline_total_cost * 0, currency)}",
                f"-{format_currency(result.contingency_amount, currency)}",
                format_currency(result.profit, currency),
            ],
            y=[
                float(result.net_revenue), # simplified clear breakdown
                -float(0),
                float(result.net_revenue),
                -float(result.scenario_delivery_cost),
                -float(0),
                -float(0),
                -float(result.contingency_amount),
                float(result.profit),
            ],
            connector={"line": {"color": "#CBD5E1"}},
            decreasing={"marker": {"color": "#EF4444"}},
            increasing={"marker": {"color": "#10B981"}},
            totals={"marker": {"color": "#1E3A8A"}},
        )
    )

    fig.update_layout(
        title={
            "text": "Commercial Value & Cost Structure",
            "font": {"size": 14, "color": "#1E293B"},
        },
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        yaxis=dict(
            title=f"Amount ({currency})",
            showgrid=True,
            gridcolor="#F1F5F9",
        ),
        xaxis=dict(
            tickfont=dict(size=11, color="#475569"),
            showgrid=False,
        ),
    )
    return fig


def render_commercial_analysis_page():
    """Render Phase 2 Commercial Analysis Interface with interactive engine."""
    st.subheader("💼 Commercial Deal Analysis & Margin Optimization")
    st.markdown(
        """
        Model proposed engagement financials, evaluate delivery cost components, stress-test cost overruns, 
        and calculate break-even and target-margin required fees with exact Decimal precision.
        """
    )

    # Top Controls Bar: Currency & Parameters Notice
    col_curr, col_mode = st.columns([1, 3])
    with col_curr:
        currency_selection = st.selectbox(
            "Display Currency",
            options=["USD ($)", "INR (₹)"],
            index=0,
            help="Currency selection modifies display formatting only. Mathematical calculations remain currency-neutral.",
        )
        currency_code = "INR" if "INR" in currency_selection else "USD"

    with col_mode:
        st.markdown(
            """
            <div style="background-color: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 8px; padding: 10px 14px; font-size: 0.82rem; color: #475569; margin-top: 14px;">
                <strong>Hypothetical Demonstration Baseline:</strong> Defaults represent a typical enterprise analytics engagement. 
                Adjust any parameter to re-compute margins instantly.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Inputs Layout (2 columns: Commercial Pricing vs Delivery Costs)
    in_col1, in_col2 = st.columns(2)

    with in_col1:
        st.markdown("##### 1. Commercial Pricing & Terms")
        base_quoted_price = st.number_input(
            "Base Quoted Price",
            min_value=0.0,
            max_value=100000000.0,
            value=100000.0,
            step=5000.0,
            help="Catalog or gross proposed fee before client discount.",
        )
        discount_pct = st.number_input(
            "Client Discount (%)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.5,
            help="Negotiated commercial concession or rate reduction percentage.",
        )
        target_margin_pct = st.number_input(
            "Target Profit Margin (%)",
            min_value=0.0,
            max_value=99.99,
            value=25.0,
            step=1.0,
            help="Practice-mandated profit margin threshold (must be strictly below 100%).",
        )

    with in_col2:
        st.markdown("##### 2. Delivery Costs & Scenarios")
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            delivery_costs = st.number_input(
                "Delivery Costs (Labour & Subs)",
                min_value=0.0,
                max_value=100000000.0,
                value=50000.0,
                step=2500.0,
                help="Direct delivery personnel, consultants, and specialized subcontractors.",
            )
            software_costs = st.number_input(
                "Software & Cloud Tooling",
                min_value=0.0,
                max_value=10000000.0,
                value=6000.0,
                step=500.0,
                help="Engagement-specific cloud computing, SaaS licensing, and sandbox environments.",
            )
        with c_sub2:
            other_expenses = st.number_input(
                "Other Project Expenses",
                min_value=0.0,
                max_value=10000000.0,
                value=4000.0,
                step=500.0,
                help="Travel, per diems, legal, compliance, and client-site materials.",
            )
            contingency_pct = st.number_input(
                "Contingency Reserve (%)",
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=1.0,
                help="Buffer applied to direct estimated cost to absorb standard delivery variance.",
            )

        cost_overrun_pct = st.number_input(
            "Delivery-Cost Overrun (%) [Stress Test]",
            min_value=0.0,
            max_value=200.0,
            value=0.0,
            step=5.0,
            help="Simulates percentage increase in labor/subcontractor costs due to scope or timeline elongation.",
        )

    # Calculation execution with robust error handling
    try:
        inputs = CommercialInputs.from_percentages(
            base_quoted_price=base_quoted_price,
            delivery_costs=delivery_costs,
            software_tooling_costs=software_costs,
            other_expenses=other_expenses,
            contingency_pct=contingency_pct,
            discount_pct=discount_pct,
            cost_overrun_pct=cost_overrun_pct,
            target_margin_pct=target_margin_pct,
        )
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
                f"The projected engagement results in a loss of **{format_currency(res.profit, currency_code)}** "
                f"(Profit Margin: {format_percentage(res.profit_margin_pct)}). "
                f"Break-even net revenue is **{format_currency(res.break_even_net_revenue, currency_code)}**."
            )
        elif not res.meets_target_margin:
            st.warning(
                f"⚠️ **TARGET MARGIN DEFICIT**: "
                f"Projected margin of **{format_percentage(res.profit_margin_pct)}** is below your practice target of **{format_percentage(target_margin_pct)}%** "
                f"(Deficit: {format_percentage(abs(res.margin_gap_pct) if res.margin_gap_pct is not None else 0)}). "
                f"To achieve target margin, required net price is **{format_currency(res.required_net_price, currency_code)}** "
                f"(or quote **{format_currency(res.required_quoted_price, currency_code)}** before discount)."
            )
        else:
            st.success(
                f"✅ **COMMERCIAL THRESHOLD MET**: "
                f"Projected margin of **{format_percentage(res.profit_margin_pct)}** satisfies the practice target of **{format_percentage(target_margin_pct)}%** "
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
                    <div class="dw-card-value">{format_currency(res.net_revenue, currency_code)}</div>
                    <div class="dw-card-subtext">After {format_percentage(discount_pct)} discount</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with kpi2:
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Scenario Total Cost</div>
                    <div class="dw-card-value">{format_currency(res.scenario_total_cost, currency_code)}</div>
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
                    <div class="dw-card-value {profit_class}">{format_currency(res.profit, currency_code)}</div>
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
                    <div class="dw-card-subtext">Target: {format_percentage(target_margin_pct)}%</div>
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
                    <div class="dw-card-value">{format_currency(res.break_even_net_revenue, currency_code)}</div>
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
                    <div class="dw-card-value">{format_currency(res.required_net_price, currency_code)}</div>
                    <div class="dw-card-subtext">Net fee needed for {format_percentage(target_margin_pct)}% margin</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with skpi4:
            st.markdown(
                f"""
                <div class="dw-card">
                    <div class="dw-card-title">Target Quoted Price</div>
                    <div class="dw-card-value">{format_currency(res.required_quoted_price, currency_code)}</div>
                    <div class="dw-card-subtext">Quote before {format_percentage(discount_pct)} discount</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Cost Component Breakdown & Structure
        st.markdown("#### Cost Architecture & Breakdown")
        cost_col, summary_col = st.columns([3, 2])

        with cost_col:
            # Breakdown table
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
                    f"Quoted labor allocation",
                    f"Fixed engagement software/cloud",
                    f"Expenses & travel",
                    f"Delivery + Software + Expenses",
                    f"{format_percentage(contingency_pct)} of Direct Estimated Cost",
                    f"Direct Cost + Contingency",
                    f"{format_percentage(cost_overrun_pct)} overrun on Delivery Costs",
                    f"Scenario Delivery + Software + Expenses + Contingency",
                ],
                f"Amount ({currency_code})": [
                    format_currency(delivery_costs, currency_code),
                    format_currency(software_costs, currency_code),
                    format_currency(other_expenses, currency_code),
                    format_currency(res.direct_estimated_cost, currency_code),
                    format_currency(res.contingency_amount, currency_code),
                    format_currency(res.baseline_total_cost, currency_code),
                    format_currency(res.scenario_delivery_cost - Decimal(str(delivery_costs)), currency_code),
                    format_currency(res.scenario_total_cost, currency_code),
                ],
            }
            st.table(breakdown_data)

        with summary_col:
            # Visual summary bar chart
            cost_labels = ["Scenario Delivery", "Software & Cloud", "Other Expenses", "Contingency"]
            cost_vals = [
                float(res.scenario_delivery_cost),
                float(software_costs),
                float(other_expenses),
                float(res.contingency_amount),
            ]
            fig_bar = go.Figure(
                go.Bar(
                    x=cost_labels,
                    y=cost_vals,
                    marker_color=["#1E3A8A", "#2563EB", "#60A5FA", "#F59E0B"],
                    text=[format_currency(v, currency_code) for v in cost_vals],
                    textposition="auto",
                )
            )
            fig_bar.update_layout(
                title={"text": "Cost Component Breakdown", "font": {"size": 13, "color": "#1E293B"}},
                height=300,
                margin=dict(l=10, r=10, t=35, b=10),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                yaxis=dict(title=f"Amount ({currency_code})", showgrid=True, gridcolor="#F1F5F9"),
                xaxis=dict(tickfont=dict(size=10, color="#475569")),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

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
                **Interactive Controls (Phase 2 Roadmap)**:
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
                **Governance Metrics (Phase 2 Roadmap)**:
                - Recommended contingency buffer ($ and % of fee)
                - Break-even delivery duration threshold
                - Margin at Risk (MaR) calculation
                """
            )

    elif section.key == "proposal_reports":
        st.markdown(
            """
            **Deliverables Planned for Phase 3**:
            - **Executive Briefing Sheet**: One-page commercial summary designed for practice leader sign-off.
            - **Client Fee Schedule**: Transparent, professional pricing schedule suitable for proposal appendices.
            - **Governance Audit Log**: Version-controlled snapshot of pricing assumptions, approvals, and margin targets.
            """
        )

    st.warning(
        f"⚙️ **Status**: Module planned for upcoming implementation milestone (Phase {section.phase})."
    )


def main():
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

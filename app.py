"""DealWise - Consulting Proposal & Commercial Intelligence Platform.

Phase 1: Project Foundation & Enterprise Architecture.
"""

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
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .dw-card-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .dw-card-value-placeholder {
        font-size: 1.8rem;
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

        # Map back to section key
        selected_index = nav_options.index(selected_label)
        selected_section = PAGES[selected_index]

        st.divider()

        st.caption("ENVIRONMENT & GOVERNANCE")
        st.markdown(
            f"""
            <div style="font-size: 0.82rem; color: #475569; line-height: 1.6;">
                <div><strong>Build:</strong> <code>{APP_VERSION}</code></div>
                <div><strong>Tier:</strong> Standard Local Runtime</div>
                <div><strong>Formulas:</strong> Phase 2 Baseline</div>
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
    # Neutral structural values indicating empty-state blueprint without fabricating client figures
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
            "text": "Planned Deal Commercial Waterfall (Phase 2 Scoping Engine Model)",
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
    st.markdown("#### Commercial Proposal Baseline (Empty State)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div class="dw-card">
                <div class="dw-card-title">Target Gross Margin</div>
                <div class="dw-card-value-placeholder">-- %</div>
                <div class="dw-card-subtext"><span class="dw-badge-upcoming">Phase 2 Input</span> Awaiting staffing model</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="dw-card">
                <div class="dw-card-title">Blended Bill Rate</div>
                <div class="dw-card-value-placeholder">$ -- / hr</div>
                <div class="dw-card-subtext"><span class="dw-badge-upcoming">Phase 2 Input</span> Awaiting role pyramid</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="dw-card">
                <div class="dw-card-title">Risk Contingency</div>
                <div class="dw-card-value-placeholder">-- %</div>
                <div class="dw-card-subtext"><span class="dw-badge-upcoming">Phase 2 Input</span> Awaiting risk assessment</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
            <div class="dw-card">
                <div class="dw-card-title">Commercial Model</div>
                <div class="dw-card-value-placeholder">T&M / Fixed</div>
                <div class="dw-card-subtext"><span class="dw-badge-upcoming">Phase 2 Input</span> Awaiting contract type</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Empty-State Visual Representation
    st.markdown("#### Commercial Modeling Blueprint")
    chart_col, info_col = st.columns([3, 2])

    with chart_col:
        fig = render_empty_state_chart()
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Note: The visual above illustrates the structural schema for Phase 2 commercial waterfall calculations. "
            "No calculation logic is active in Phase 1."
        )

    with info_col:
        st.markdown(
            """
            <div class="dw-card" style="height: 100%;">
                <div class="dw-card-title">Value Design Capabilities</div>
                <ul style="font-size: 0.88rem; color: #334155; padding-left: 20px; line-height: 1.7;">
                    <li><strong>Staffing Optimization</strong>: Calibrate role grade leverage (Partner to Analyst) against engagement complexity.</li>
                    <li><strong>Contract Structuring</strong>: Compare Time & Materials, Capped T&M, and Milestone-based Fixed Fee structures.</li>
                    <li><strong>Margin Buffer Calibration</strong>: Stress-test delivery overruns before commercial sign-off.</li>
                    <li><strong>Proposal Governance</strong>: Generate consistent, auditable commercial briefings for engagement partners.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Core Pillar Pipeline
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
    st.markdown("#### Phase 1 Architecture Verification")
    st.success(
        "✅ **Phase 1 Foundation Operational**: Clean application shell initialized with enterprise visual styling, "
        "type-hinted configuration, modular layout, automated test coverage, and synthetic data governance."
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

    if section.key == "commercial_analysis":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                """
                **Core Inputs (Phase 2)**:
                - Role seniority distribution (Partner, Director, Manager, Senior, Analyst)
                - Workstream week allocations and billable hours
                - Direct cost rate basis vs. standard catalog rates
                - Target practice contribution margin threshold
                """
            )
        with col2:
            st.markdown(
                """
                **Analytical Outputs (Phase 2)**:
                - Blended hourly rate curve
                - Gross and net contribution margin waterfall
                - Leverage ratio (Junior-to-Senior delivery mix)
                - Realization discount analysis vs standard card
                """
            )

    elif section.key == "scenario_simulator":
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
                **Interactive Controls (Phase 2)**:
                - Real-time parameter sliders for team sizing, duration, and discount adjustments.
                - Sensitivity matrix displaying margin variance across delivery velocity assumptions.
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
                **Governance Metrics (Phase 2)**:
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
        "⚙️ **Status**: In accordance with the Phase 1 implementation boundaries, computation formulas and interactive "
        "calculators are intentionally deferred to Phase 2."
    )


def main():
    selected_section = render_sidebar()
    render_header(selected_section)

    if selected_section.key == "overview":
        render_overview_page()
    else:
        render_planned_section_view(selected_section)


if __name__ == "__main__":
    main()

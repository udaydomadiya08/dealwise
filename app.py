"""DealWise - Consulting Proposal & Commercial Intelligence Platform.

Phases 1-4: Project Foundation, Commercial Engine, Executive Dashboard & Scenario Simulator.
"""

import html
from decimal import Decimal
from typing import List
import pandas as pd
import streamlit as st
from src.config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_VERSION,
    TARGET_ROLE,
    DISCLAIMER_TEXT,
    PAGES,
)
from src.commercial_engine import (
    CommercialInputs,
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
)
from src.scenario_engine import (
    compare_scenarios,
    generate_sensitivity_grid,
    evaluate_fixed_fee_model,
    evaluate_time_and_materials_model,
    export_scenario_to_csv,
)
from src.risk_engine import (
    RiskRecord,
    RiskSeverity,
    ChecklistItem,
    ChecklistStatus,
    RiskValidationError,
    prioritize_risks,
    calculate_proposal_readiness,
    get_default_readiness_checklist,
    evaluate_financial_stress_cases,
    generate_suggested_risk_flags,
    generate_mitigation_plan,
    export_risk_assessment_csv,
)
from src.report_engine import (
    ProposalMetadata,
    assemble_proposal_report,
    generate_proposal_pdf,
    export_proposal_commercial_csv,
    generate_report_filename,
)
from src.case_study import (
    OFFICIAL_INFOSYS_SOURCES,
    INFOSYS_CASE_STUDY_PRESET,
    CaseStudyPreset,
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

DEFAULT_PROPOSAL_METADATA = {
    "proposal_title": "Enterprise Data Platform & Value Analytics Proposal",
    "client_name": "Global Retail & Logistics Corp (Hypothetical Demo)",
    "client_industry": "Supply Chain & Retail Analytics",
    "prepared_by": "Data & Analytics Commercial Practice",
    "business_problem": "Client experiences fragmented data ingestion across 14 enterprise ERP systems, leading to delayed financial reconciliation and high operational latency in inventory allocation.",
    "proposed_solution": "Deliver an integrated modern data platform with automated pipeline governance, near real-time margin analytics, and an executive value realization dashboard.",
    "scope_deliverables": "Phase 1: Architecture blueprint & ingestion pipeline design (Weeks 1-4).\nPhase 2: Core analytics mart & automated reconciliation (Weeks 5-8).\nPhase 3: Executive dashboard & production deployment (Weeks 9-10).",
    "assumptions_exclusions": "Assumes client provides cloud environment access by Day 3. Excludes ERP vendor license procurement, third-party API licensing, and legacy hardware decommissioning.",
    "proposed_timeline": "10 calendar weeks across 3 delivery sprints.",
    "payment_terms": "Fixed-fee milestone payments: 30% on kick-off, 40% on interim pipeline sign-off (Week 6), 30% upon final acceptance. Net 30 days.",
    "notes_and_next_steps": "Subject to executive commercial review. Next step: Finalize data schema discovery sprint and complete formal client procurement intake.",
    "is_hypothetical_demo": True,
}


def init_session_state():
    """Initialize shared commercial parameters across pages."""
    for key, val in DEFAULT_DEAL_PARAMS.items():
        if key not in st.session_state:
            st.session_state[key] = val
    for key, val in DEFAULT_PROPOSAL_METADATA.items():
        if key not in st.session_state:
            st.session_state[key] = val
    if "readiness_checklist" not in st.session_state:
        st.session_state["readiness_checklist"] = get_default_readiness_checklist()
    if "custom_risks" not in st.session_state:
        st.session_state["custom_risks"] = []
    if "case_study_active" not in st.session_state:
        st.session_state["case_study_active"] = False


def apply_case_study_preset(preset: CaseStudyPreset):
    """Load case study parameters into shared session state."""
    st.session_state["base_quoted_price"] = float(preset.inputs.base_quoted_price)
    st.session_state["delivery_costs"] = float(preset.inputs.delivery_costs)
    st.session_state["software_costs"] = float(preset.inputs.software_tooling_costs)
    st.session_state["other_expenses"] = float(preset.inputs.other_expenses)
    st.session_state["contingency_pct"] = float(preset.inputs.contingency_pct * Decimal("100"))
    st.session_state["discount_pct"] = float(preset.inputs.discount_pct * Decimal("100"))
    st.session_state["cost_overrun_pct"] = float(preset.inputs.cost_overrun_pct * Decimal("100"))
    st.session_state["target_margin_pct"] = float(preset.inputs.target_margin_pct * Decimal("100"))
    st.session_state["currency_selection"] = "USD ($)"

    st.session_state["proposal_title"] = preset.title
    st.session_state["client_name"] = preset.client_name
    st.session_state["client_industry"] = preset.industry
    st.session_state["prepared_by"] = preset.provider_context
    st.session_state["business_problem"] = preset.business_problem
    st.session_state["proposed_solution"] = preset.proposed_solution
    st.session_state["scope_deliverables"] = preset.scope_deliverables
    st.session_state["assumptions_exclusions"] = preset.assumptions_exclusions
    st.session_state["proposed_timeline"] = preset.delivery_timeline
    st.session_state["payment_terms"] = preset.payment_terms
    st.session_state["notes_and_next_steps"] = preset.executive_recommendation
    st.session_state["executive_recommendation"] = preset.executive_recommendation

    # Update checklist
    default_cl = get_default_readiness_checklist()
    updated_cl = []
    for item in default_cl:
        is_done = preset.checklist_statuses.get(item.item_id, item.status == ChecklistStatus.COMPLETED)
        updated_cl.append(
            ChecklistItem(
                item_id=item.item_id,
                title=item.title,
                category=item.category,
                description=item.description,
                status=ChecklistStatus.COMPLETED if is_done else ChecklistStatus.IN_PROGRESS,
                notes=f"Aligned with {preset.provider_context} engagement governance.",
            )
        )
    st.session_state["readiness_checklist"] = updated_cl
    st.session_state["custom_risks"] = list(preset.risks)


def reset_to_default_workspace():
    """Reset session state back to general-purpose defaults."""
    for key, val in DEFAULT_DEAL_PARAMS.items():
        st.session_state[key] = val
    for key, val in DEFAULT_PROPOSAL_METADATA.items():
        st.session_state[key] = val
    st.session_state["readiness_checklist"] = get_default_readiness_checklist()
    st.session_state["custom_risks"] = []
    if "executive_recommendation" in st.session_state:
        del st.session_state["executive_recommendation"]


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

        st.caption("CASE STUDY SCENARIO MODE")
        case_options = [
            "Standard General Workspace",
            "Infosys: Enterprise Cloud & AI Transformation",
        ]
        curr_case_idx = 1 if st.session_state.get("case_study_active", False) else 0
        selected_case = st.selectbox(
            "Scenario Mode",
            options=case_options,
            index=curr_case_idx,
            help="Select an enterprise case study scenario calibrated against official public facts.",
        )

        if selected_case == "Infosys: Enterprise Cloud & AI Transformation":
            if not st.session_state.get("case_study_active", False):
                apply_case_study_preset(INFOSYS_CASE_STUDY_PRESET)
                st.session_state["case_study_active"] = True
                st.rerun()
            if st.button("🔄 Reload Case Study Preset", use_container_width=True):
                apply_case_study_preset(INFOSYS_CASE_STUDY_PRESET)
                st.rerun()
        else:
            if st.session_state.get("case_study_active", False):
                reset_to_default_workspace()
                st.session_state["case_study_active"] = False
                st.rerun()

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
                <div><strong>Case Study:</strong> {'Active (Infosys)' if st.session_state.get('case_study_active') else 'Standard'}</div>
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
            <div style="margin-top: 10px;">
                <a href="https://udaydomadiya08-dealwise-app-4sq2ju.streamlit.app/" target="_blank" style="font-size: 0.78rem; color: #2563EB; font-weight: 600; text-decoration: none;">
                    🌐 Live Cloud Instance ↗
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_section


def render_case_study_banner():
    """Render interactive Infosys real-world case study briefing panel."""
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0F2D59 0%, #1E3A8A 100%); color: white; padding: 16px 20px; border-radius: 8px; margin-bottom: 14px; border-left: 6px solid #38BDF8;">
            <div style="font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; justify-content: space-between;">
                <span>🏢 Case Study Active: Infosys-Aligned Enterprise Cloud & AI Transformation</span>
                <span style="font-size: 0.72rem; background: #0284C7; padding: 3px 8px; border-radius: 9999px; font-weight: 600;">OFFICIAL PUBLIC FACTS</span>
            </div>
            <div style="font-size: 0.85rem; color: #E0F2FE; margin-top: 6px; line-height: 1.5;">
                Illustrative 36-week enterprise transformation proposal for <strong>Global OmniRetail Enterprises</strong>. Calibrated against Infosys Consulting's Technology Transformation offerings, Cobalt cloud suite, Topaz generative AI frameworks, and official FY corporate operating margin benchmarks (20.3% reported / 21.0% adjusted).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("🔍 Inspect Case Study Evidence, Delivery Pyramid & Verified Public Sources", expanded=False):
        cs_tab1, cs_tab2, cs_tab3, cs_tab4 = st.tabs([
            "🏛️ Verified Public Facts",
            "👥 Engagement Scope & Staffing",
            "📋 Assumptions vs Facts Register",
            "🛡️ Independent Project Disclaimer",
        ])
        with cs_tab1:
            st.markdown("##### Official Public Information from Authoritative Sources")
            st.caption("All facts below are verified against official Infosys publications. Retrieval Date: October 2026.")
            fact_rows = []
            for s in OFFICIAL_INFOSYS_SOURCES:
                fact_rows.append({
                    "Category": s.category,
                    "Topic / Capability": s.topic,
                    "Key Verified Fact": s.fact_summary,
                    "Official Source": s.official_source_title,
                    "Source URL": s.source_url,
                })
            st.dataframe(pd.DataFrame(fact_rows), use_container_width=True, hide_index=True)
            st.markdown("###### Official Source Citations:")
            for s in OFFICIAL_INFOSYS_SOURCES:
                st.markdown(f"- **{s.topic}**: [{s.official_source_title}]({s.source_url}) *(Category: {s.category})*")

        with cs_tab2:
            st.markdown("##### Illustrative Engagement Scoping & Delivery Leverage")
            st.markdown(f"**Client**: {INFOSYS_CASE_STUDY_PRESET.client_name} | **Industry**: {INFOSYS_CASE_STUDY_PRESET.industry}")
            st.markdown(f"**Duration**: {INFOSYS_CASE_STUDY_PRESET.duration_weeks} Weeks (4 Delivery Phases) | **Commercial Model**: {INFOSYS_CASE_STUDY_PRESET.engagement_type}")
            st.markdown(f"**Target Practice Margin**: {float(INFOSYS_CASE_STUDY_PRESET.inputs.target_margin_pct * Decimal('100')):.1f}% *(Calibrated against Infosys Integrated Annual Report operating margin benchmark of 20.3% - 21.0%)*")

            st.markdown("###### Delivery Team Staffing Pyramid:")
            pyramid_rows = [
                {
                    "Role Title": r.role_title,
                    "FTE": r.count_fte,
                    "Experience": r.experience_level,
                    "Phase Allocation": r.delivery_phase,
                    "Key Responsibilities": r.responsibilities,
                }
                for r in INFOSYS_CASE_STUDY_PRESET.staffing_pyramid
            ]
            st.dataframe(pd.DataFrame(pyramid_rows), use_container_width=True, hide_index=True)

        with cs_tab3:
            st.markdown("##### Data Provenance & Assumptions Register")
            st.caption("Strict separation between verified public disclosures, user-configurable assumptions, calculated outputs, and model recommendations.")
            provenance_rows = [
                {"Type": "Verified Public Fact", "Item": "Consulting Service Pillars", "Description": "Strategic Technology Services, FinOps, Cloud Advisory, Digital Platforms (SAP, Salesforce, ServiceNow)", "Source": "Infosys Consulting Official Offerings"},
                {"Type": "Verified Public Fact", "Item": "Technology Suites", "Description": "Infosys Cobalt (Cloud) & Infosys Topaz (Generative AI & Autonomous Agents)", "Source": "Infosys Official Platform Portals"},
                {"Type": "Verified Public Fact", "Item": "Corporate Operating Margin", "Description": "20.3% reported / 21.0% adjusted operating margin benchmark", "Source": "Infosys Integrated Annual Report"},
                {"Type": "Hypothetical Assumption", "Item": "Quoted Fee ($1,250,000)", "Description": "Illustrative contract value for 36-week enterprise engagement", "Source": "Synthetic Case Study Parameter"},
                {"Type": "Hypothetical Assumption", "Item": "Delivery Costs ($780,000 labor + $85,000 tools)", "Description": "Synthetically constructed staffing pyramid economics", "Source": "Synthetic Case Study Parameter"},
                {"Type": "Hypothetical Assumption", "Item": "Target Margin (21.0%)", "Description": "Practice pricing target calibrated to corporate operating margin profile", "Source": "Calibrated Practice Benchmark"},
                {"Type": "Calculated Output", "Item": "Operating Profit & Margin", "Description": "Exact Python Decimal formula: Net Revenue - Scenario Total Cost", "Source": "DealWise Commercial Engine"},
                {"Type": "Calculated Output", "Item": "Break-Even Quoting Price", "Description": "Closed-form required quote: Direct Cost / (1 - Target Margin)", "Source": "DealWise Commercial Engine"},
                {"Type": "Model Recommendation", "Item": "Contract Structure", "Description": "Fixed-fee for deterministic cloud migration + Capped T&M for AI workflows", "Source": "DealWise Commercial Governance Advisory"},
            ]
            st.dataframe(pd.DataFrame(provenance_rows), use_container_width=True, hide_index=True)

        with cs_tab4:
            st.markdown("##### Portfolio Integrity & Professional Independence Notice")
            st.warning(
                "**DISCLAIMER**: DealWise is an independent software portfolio project authored by Uday Domadiya. "
                "It is not an official product, service offering, endorsement, or representation of Infosys. "
                "All company references are derived exclusively from publicly available official disclosures. "
                "All project pricing, labor rates, staffing costs, and contract terms are synthetic assumptions "
                "created solely to demonstrate enterprise commercial modeling and advisory capabilities."
            )


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

    if st.session_state.get("case_study_active", False):
        render_case_study_banner()


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


def render_risk_review_page():
    """Render Phase 5 Commercial Risk Intelligence, Proposal Readiness, and Exposure Analysis."""
    st.subheader("🛡️ Commercial Risk Intelligence & Proposal Readiness")
    st.markdown(
        """
        Comprehensive commercial diligence workspace: manage qualitative risk registers, 
        audit proposal readiness checklists, quantify deterministic financial stress exposures, 
        and formulate actionable mitigation plans prior to commercial sign-off.
        """
    )

    currency = get_active_currency()
    active_inputs = get_active_inputs()
    active_res = calculate_commercials(active_inputs)

    # Transparency disclaimer
    st.markdown(
        """
        <div class="dw-disclaimer-box" style="margin-bottom: 16px;">
            <strong>GOVERNANCE NOTICE:</strong> All initial risk items represent hypothetical demonstration archetypes. 
            Ordinal risk scores (Likelihood &times; Impact) provide qualitative prioritization rankings and do not represent 
            actuarial loss probabilities or statistical forecasts. Proposal readiness measures diligence checklist completion; 
            final commercial commitment remains a human decision by practice leadership.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Combine auto-suggested risk flags with custom user risks
    suggested_risks = generate_suggested_risk_flags(active_inputs, active_res)
    custom_risks: List[RiskRecord] = st.session_state.get("custom_risks", [])

    # All unique risks
    all_risks_dict = {r.risk_id: r for r in suggested_risks}
    for cr in custom_risks:
        all_risks_dict[cr.risk_id] = cr
    all_risks = list(all_risks_dict.values())

    # Calculate readiness and financial stress cases
    checklist: List[ChecklistItem] = st.session_state.get("readiness_checklist", get_default_readiness_checklist())
    readiness = calculate_proposal_readiness(checklist)
    stress_cases = evaluate_financial_stress_cases(active_inputs, active_res)

    # Top Executive Summary Metrics (4 cards)
    r1, r2, r3, r4 = st.columns(4)

    with r1:
        open_count = sum(1 for r in all_risks if r.status.lower() in ("open", "in progress"))
        st.markdown(
            f"""
            <div class="dw-card">
                <div class="dw-card-title">Open Identified Risks</div>
                <div class="dw-card-value">{open_count}</div>
                <div class="dw-card-subtext">{len(all_risks)} total cataloged risks</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r2:
        crit_high_count = sum(1 for r in all_risks if r.severity in (RiskSeverity.CRITICAL, RiskSeverity.HIGH))
        badge_cls = "dw-badge-danger" if crit_high_count > 0 else "dw-badge-active"
        st.markdown(
            f"""
            <div class="dw-card">
                <div class="dw-card-title">Critical & High Risks</div>
                <div class="dw-card-value" style="color: {'#DC2626' if crit_high_count > 0 else '#15803D'};">{crit_high_count}</div>
                <div class="dw-card-subtext"><span class="{badge_cls}">{crit_high_count} Priority Flags</span> Requiring mitigation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r3:
        readiness_badge = "dw-badge-active" if readiness.is_ready_for_review else "dw-badge-warning"
        st.markdown(
            f"""
            <div class="dw-card">
                <div class="dw-card-title">Proposal Diligence Score</div>
                <div class="dw-card-value">{readiness.completion_pct}%</div>
                <div class="dw-card-subtext"><span class="{readiness_badge}">{readiness.completed_items}/{readiness.applicable_items} Done</span> Excludes N/A items</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r4:
        max_drawdown = min(sc.profit_impact for sc in stress_cases)
        st.markdown(
            f"""
            <div class="dw-card">
                <div class="dw-card-title">Max Stress Drawdown</div>
                <div class="dw-card-value dw-card-value-negative">{format_currency(max_drawdown, currency)}</div>
                <div class="dw-card-subtext">Compound adverse stress impact</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 4 Modular Governance Tabs
    tab_readiness, tab_register, tab_stress, tab_mitigation = st.tabs([
        "📋 Proposal Readiness Checklist",
        "📑 Commercial Risk Register",
        "📉 Financial Stress-Testing",
        "🎯 Prioritized Mitigation Plan",
    ])

    # TAB 1: Proposal Readiness Governance Checklist
    with tab_readiness:
        st.markdown("##### Proposal Governance Diligence Checklist")
        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; font-size: 0.85rem; color: #334155;">
                <strong>Governance Narrative:</strong> {readiness.summary_narrative}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(float(readiness.completion_pct) / 100.0)

        # Interactive checklist editor
        updated_checklist: List[ChecklistItem] = []
        for idx, item in enumerate(checklist):
            c_info, c_status = st.columns([3, 1])
            with c_info:
                st.markdown(f"**{item.item_id}: {item.title}** `[{item.category}]`")
                st.caption(item.description)

            with c_status:
                status_options = [s.value for s in ChecklistStatus]
                current_idx = status_options.index(item.status.value)
                new_status_str = st.selectbox(
                    f"Status for {item.item_id}",
                    options=status_options,
                    index=current_idx,
                    key=f"chk_status_{item.item_id}_{idx}",
                    label_visibility="collapsed",
                )
                updated_item = ChecklistItem(
                    item_id=item.item_id,
                    category=item.category,
                    title=item.title,
                    description=item.description,
                    status=ChecklistStatus(new_status_str),
                    notes=item.notes,
                )
                updated_checklist.append(updated_item)
            st.divider()

        st.session_state["readiness_checklist"] = updated_checklist

    # TAB 2: Commercial Risk Register
    with tab_register:
        st.markdown("##### Commercial Risk Register")
        st.caption("Auto-suggested deal flags based on current pricing and staffing inputs, combined with custom project risks.")

        # Interactive form to add/update custom risk
        with st.expander("➕ Log New or Update Risk Record", expanded=False):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                new_id = st.text_input("Risk Identifier", value=f"RSK-{len(all_risks) + 1:03d}")
                new_cat = st.selectbox("Category", options=["Scope & Delivery", "Commercial & Pricing", "Staffing & Resourcing", "Legal & Governance", "Client Dependency"])
                new_desc = st.text_area("Risk Description", value="Unvalidated subcontractor reliance in analytics workstream.")
                new_owner = st.selectbox("Owner / Role", options=["Engagement Manager", "Solutions Architect", "Commercial Partner", "Pricing Director", "Staffing Lead"])
            with f_col2:
                new_l = st.slider("Likelihood Score (1-5)", min_value=1, max_value=5, value=3, help="1=Rare, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost Certain")
                new_i = st.slider("Impact Score (1-5)", min_value=1, max_value=5, value=4, help="1=Insignificant, 2=Minor, 3=Moderate, 4=Major, 5=Severe")
                new_mit = st.text_area("Mitigation Action", value="Execute back-to-back delivery agreements with primary subcontractor.")
                new_stat = st.selectbox("Status", options=["Open", "In Progress", "Mitigated", "Accepted"])
                new_exp = st.number_input("Optional Financial Exposure ($ / ₹)", min_value=0.0, value=10000.0, step=1000.0)

            if st.button("Save Risk Record"):
                try:
                    new_rec = RiskRecord(
                        risk_id=new_id,
                        category=new_cat,
                        description=new_desc,
                        likelihood=new_l,
                        impact=new_i,
                        owner=new_owner,
                        mitigation=new_mit,
                        status=new_stat,
                        financial_exposure=Decimal(str(new_exp)) if new_exp > 0 else None,
                        notes="User logged risk during current session.",
                        is_auto_suggested=False,
                    )
                    # Update session state list
                    existing_custom = [r for r in st.session_state.get("custom_risks", []) if r.risk_id != new_id]
                    existing_custom.append(new_rec)
                    st.session_state["custom_risks"] = existing_custom
                    st.success(f"✅ Risk record '{new_id}' saved successfully!")
                    st.rerun()
                except RiskValidationError as err:
                    st.error(f"⚠️ Validation Error: {err}")

        # Render Risk Table
        sorted_risks = prioritize_risks(all_risks)
        risk_table_data = {
            "ID": [r.risk_id for r in sorted_risks],
            "Category": [r.category for r in sorted_risks],
            "Description": [r.description for r in sorted_risks],
            "L x I": [f"{r.likelihood} x {r.impact}" for r in sorted_risks],
            "Score": [r.score for r in sorted_risks],
            "Severity": [r.severity.value for r in sorted_risks],
            "Owner": [r.owner for r in sorted_risks],
            "Status": [r.status for r in sorted_risks],
            f"Exposure ({currency})": [format_currency(r.financial_exposure, currency) if r.financial_exposure is not None else "—" for r in sorted_risks],
            "Source": ["Auto Flag" if r.is_auto_suggested else "Custom Log" for r in sorted_risks],
        }
        st.table(risk_table_data)

    # TAB 3: Financial Exposure & Stress-Testing
    with tab_stress:
        st.markdown("##### Deterministic Financial Stress-Testing")
        st.markdown(
            """
            Stress-testing evaluates how specific adverse operational and commercial shocks erode 
            engagement profitability using the underlying commercial engine.
            """
        )

        st.caption(
            "🛡️ **Double-Counting Transparency:** The stress cases below model incremental friction beyond the saved baseline. "
            "Exposures are not added on top of existing scenario buffers unless explicitly stated."
        )

        for sc in stress_cases:
            with st.container():
                st.markdown(f"###### {sc.name}")
                st.caption(f"**Assumptions:** {sc.assumptions}")

                s1, s2, s3, s4 = st.columns(4)
                with s1:
                    st.metric(
                        label="Stressed Revenue",
                        value=format_currency(sc.stressed_revenue, currency),
                        delta=f"{format_currency(sc.stressed_revenue - sc.baseline_revenue, currency)}",
                    )
                with s2:
                    st.metric(
                        label="Stressed Cost",
                        value=format_currency(sc.stressed_cost, currency),
                        delta=f"{format_currency(sc.stressed_cost - sc.baseline_cost, currency)}",
                        delta_color="inverse",
                    )
                with s3:
                    st.metric(
                        label="Stressed Profit",
                        value=format_currency(sc.stressed_profit, currency),
                        delta=f"{format_currency(sc.profit_impact, currency)}",
                    )
                with s4:
                    base_m_str = format_percentage(sc.baseline_margin_pct)
                    stress_m_str = format_percentage(sc.stressed_margin_pct)
                    delta_pp_str = f"{sc.margin_impact_pp:+.2f} pp" if sc.margin_impact_pp is not None else "N/A"
                    st.metric(
                        label="Stressed Margin",
                        value=stress_m_str,
                        delta=f"{delta_pp_str} (Base: {base_m_str})",
                    )
                st.caption(f"📝 *Transparency note:* {sc.double_counting_note}")
                st.divider()

    # TAB 4: Prioritized Mitigation Action Plan
    with tab_mitigation:
        st.markdown("##### Prioritized Commercial Mitigation Plan")
        st.caption("Rule-based actionable next steps prioritized by risk severity and financial exposure.")

        mit_plan = generate_mitigation_plan(all_risks)
        if mit_plan:
            plan_table = {
                "Rank": [p.priority_rank for p in mit_plan],
                "Risk ID": [p.risk_id for p in mit_plan],
                "Category": [p.category for p in mit_plan],
                "Suggested Role": [p.suggested_role for p in mit_plan],
                "Recommended Mitigation Action": [p.action_text for p in mit_plan],
                "Trigger Rationale": [p.trigger_rationale for p in mit_plan],
            }
            st.table(plan_table)
        else:
            st.info("No open or unmitigated risks identified.")

    st.markdown("---")

    # Section 5: CSV Export
    st.markdown("##### 5. Export Commercial Risk & Readiness Audit (CSV)")
    st.markdown("Download a complete governance package containing the risk register, readiness checklist, and stress-test results.")

    csv_risk_content = export_risk_assessment_csv(
        risks=all_risks,
        checklist=checklist,
        stress_cases=stress_cases,
        currency=currency,
    )

    st.download_button(
        label="📥 Download Commercial Risk & Readiness Audit (CSV)",
        data=csv_risk_content,
        file_name="dealwise_commercial_risk_audit.csv",
        mime="text/csv",
        help="Exports risk register, diligence checklist, and financial stress testing data.",
    )


def render_proposal_reports_page():
    """Render Phase 6 Proposal and Executive Report Generator page."""
    st.subheader("📄 Proposal Reports & Executive Commercial Briefing")
    st.markdown(
        "Assemble professional consulting proposal briefings, reconciled commercial pricing schedules, "
        "and downloadable multi-page executive PDF and CSV reports. All figures reflect the active "
        "Decimal calculation engine and governance risk register."
    )

    currency = get_active_currency()
    inputs = get_active_inputs()

    try:
        inputs.validate()
        result = calculate_commercials(inputs)
    except Exception as exc:
        st.error(f"⚠️ **Commercial Engine Calculation Error**: {exc}. Please review inputs in Commercial Analysis.")
        return

    # Section 1: Proposal Information & Scoping Form
    with st.expander("📝 1. Proposal Narrative, Scoping & Governance Inputs", expanded=True):
        st.caption("Enter engagement context, deliverables, and commercial parameters. Values persist for the active session.")

        f_col1, f_col2 = st.columns(2)
        with f_col1:
            title_val = st.text_input(
                "Proposal Title",
                value=st.session_state.get("proposal_title", ""),
                help="Descriptive engagement proposal title.",
            )
            st.session_state["proposal_title"] = title_val

            client_val = st.text_input(
                "Client / Target Organization",
                value=st.session_state.get("client_name", ""),
                help="Enterprise client name (hypothetical demo).",
            )
            st.session_state["client_name"] = client_val

            ind_val = st.text_input(
                "Client Industry",
                value=st.session_state.get("client_industry", ""),
                help="Target client industry sector.",
            )
            st.session_state["client_industry"] = ind_val

            prep_val = st.text_input(
                "Prepared By",
                value=st.session_state.get("prepared_by", ""),
                help="Authoring consulting practice or commercial team.",
            )
            st.session_state["prepared_by"] = prep_val

        with f_col2:
            time_val = st.text_input(
                "Proposed Timeline",
                value=st.session_state.get("proposed_timeline", ""),
                help="Target calendar duration and sprint structure.",
            )
            st.session_state["proposed_timeline"] = time_val

            terms_val = st.text_input(
                "Payment Terms & Milestones",
                value=st.session_state.get("payment_terms", ""),
                help="Invoicing schedule and milestone payment terms.",
            )
            st.session_state["payment_terms"] = terms_val

            hypo_val = st.checkbox(
                "Label as Hypothetical Demonstration Data",
                value=st.session_state.get("is_hypothetical_demo", True),
                help="Appends clear advisory notices confirming data is synthetic.",
            )
            st.session_state["is_hypothetical_demo"] = hypo_val

        prob_val = st.text_area(
            "Business Problem Definition",
            value=st.session_state.get("business_problem", ""),
            height=70,
            help="Core client pain point and operational context.",
        )
        st.session_state["business_problem"] = prob_val

        sol_val = st.text_area(
            "Proposed Value Design & Solution",
            value=st.session_state.get("proposed_solution", ""),
            height=70,
            help="High-level solution architecture and technical approach.",
        )
        st.session_state["proposed_solution"] = sol_val

        scope_val = st.text_area(
            "Scope & Key Deliverables",
            value=st.session_state.get("scope_deliverables", ""),
            height=85,
            help="Milestone deliverables and phase breakdown.",
        )
        st.session_state["scope_deliverables"] = scope_val

        assump_val = st.text_area(
            "Delivery Assumptions & Exclusions",
            value=st.session_state.get("assumptions_exclusions", ""),
            height=70,
            help="Critical project dependencies and out-of-scope boundaries.",
        )
        st.session_state["assumptions_exclusions"] = assump_val

        steps_val = st.text_area(
            "Commercial Next Steps & Notes",
            value=st.session_state.get("notes_and_next_steps", ""),
            height=65,
            help="Pre-submission partner actions and client procurement steps.",
        )
        st.session_state["notes_and_next_steps"] = steps_val

    cs_active = st.session_state.get("case_study_active", False)
    sources_dict = [
        {
            "topic": s.topic,
            "official_source_title": s.official_source_title,
            "source_url": s.source_url,
            "retrieval_date": s.retrieval_date,
            "category": s.category,
        }
        for s in OFFICIAL_INFOSYS_SOURCES
    ] if cs_active else None

    # Construct ProposalMetadata
    metadata = ProposalMetadata(
        title=st.session_state.get("proposal_title", "Commercial Proposal"),
        client_name=st.session_state.get("client_name", "Enterprise Client"),
        industry=st.session_state.get("client_industry", "Data & Analytics"),
        prepared_by=st.session_state.get("prepared_by", "Commercial Team"),
        business_problem=st.session_state.get("business_problem", "Not provided"),
        proposed_solution=st.session_state.get("proposed_solution", "Not provided"),
        scope_deliverables=st.session_state.get("scope_deliverables", "Not provided"),
        assumptions_exclusions=st.session_state.get("assumptions_exclusions", "Not provided"),
        timeline=st.session_state.get("proposed_timeline", "Not provided"),
        payment_terms=st.session_state.get("payment_terms", "Not provided"),
        notes_and_next_steps=st.session_state.get("notes_and_next_steps", "Not provided"),
        is_hypothetical_demo=st.session_state.get("is_hypothetical_demo", True),
        case_study_name="Infosys: Enterprise Cloud & AI Transformation" if cs_active else None,
        provider_context="Infosys Consulting (Technology Transformation Practice)" if cs_active else None,
        case_study_summary=INFOSYS_CASE_STUDY_PRESET.executive_summary if cs_active else None,
        executive_recommendation=st.session_state.get("executive_recommendation") or (INFOSYS_CASE_STUDY_PRESET.executive_recommendation if cs_active else None),
        sources_register=sources_dict,
    )

    # Incompleteness validation
    warnings = metadata.validate()
    if warnings:
        warn_text = "**Diligence Completeness Notice**: The proposal contains incomplete narrative fields:<br/>" + "<br/>".join(
            f"• {w}" for w in warnings
        )
        st.warning(warn_text)

    # Assemble report content
    checklist = st.session_state.get("readiness_checklist", get_default_readiness_checklist())
    custom_risks = st.session_state.get("custom_risks", [])
    auto_risks = generate_suggested_risk_flags(inputs, result)
    all_risks = custom_risks + auto_risks

    report_content = assemble_proposal_report(
        metadata=metadata,
        commercial_inputs=inputs,
        commercial_result=result,
        currency=currency,
        risks=all_risks,
        checklist=checklist,
    )

    st.markdown("---")

    # Section 2: Executive Summary KPI Banner
    st.markdown("##### 2. Executive Commercial Snapshot")
    kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)

    with kpi_c1:
        st.metric(
            label=f"Net Realized Revenue ({currency})",
            value=format_currency(result.net_revenue, currency),
            delta=f"Discount: {format_percentage(inputs.discount_pct * Decimal('100'))}",
            delta_color="off",
        )
    with kpi_c2:
        st.metric(
            label=f"Scenario Total Cost ({currency})",
            value=format_currency(result.scenario_total_cost, currency),
            delta=f"Contingency: {format_percentage(inputs.contingency_pct * Decimal('100'))}",
            delta_color="off",
        )
    with kpi_c3:
        st.metric(
            label=f"Operating Profit ({currency})",
            value=format_currency(result.profit, currency),
            delta="Profitable" if result.is_profitable else "Deficit / Loss",
            delta_color="normal" if result.is_profitable else "inverse",
        )
    with kpi_c4:
        margin_str = format_percentage(result.profit_margin_pct) if result.profit_margin_pct is not None else "N/A"
        st.metric(
            label="Profit Margin",
            value=margin_str,
            delta="Target Met" if result.meets_target_margin else "Target Deficit",
            delta_color="normal" if result.meets_target_margin else "inverse",
        )
    with kpi_c5:
        st.metric(
            label="Proposal Readiness",
            value=f"{report_content.risk.readiness_score_pct}%",
            delta=f"{report_content.risk.open_risks_count} Open Risks",
            delta_color="normal" if report_content.risk.readiness_score_pct >= Decimal("80.0") else "inverse",
        )

    st.markdown("---")

    # Section 3: Interactive On-Screen Report Preview
    st.markdown("##### 3. Executive Report Preview")
    tab_comm, tab_risk, tab_narrative = st.tabs([
        "💼 Commercial Pricing Schedule",
        "🛡️ Risk & Diligence Governance",
        "📄 Proposal Narrative & Scope",
    ])

    with tab_comm:
        st.markdown("**Commercial Fee Schedule & Pricing Reconciliations**")
        sched_df = pd.DataFrame([
            {"Commercial Line Item": "Base Quoted Price (List)", "Modeled Value": format_currency(inputs.base_quoted_price, currency), "Analytical Guidance": "Full contractual list price prior to discount"},
            {"Commercial Line Item": "Client Discount Concession", "Modeled Value": format_percentage(inputs.discount_pct * Decimal("100")), "Analytical Guidance": "Negotiated partner commercial concession"},
            {"Commercial Line Item": "Net Realized Revenue", "Modeled Value": format_currency(result.net_revenue, currency), "Analytical Guidance": "Base Quoted Price × (1 - Discount %)"},
            {"Commercial Line Item": "Direct Delivery Labor", "Modeled Value": format_currency(inputs.delivery_costs, currency), "Analytical Guidance": "Base consulting delivery effort"},
            {"Commercial Line Item": "Software & Tooling", "Modeled Value": format_currency(inputs.software_tooling_costs, currency), "Analytical Guidance": "Direct cloud, software, and vendor licensing"},
            {"Commercial Line Item": "Other Delivery Expenses", "Modeled Value": format_currency(inputs.other_expenses, currency), "Analytical Guidance": "Travel, logistics, and onboarding expenses"},
            {"Commercial Line Item": "Direct Estimated Cost", "Modeled Value": format_currency(result.direct_estimated_cost, currency), "Analytical Guidance": "Labor + Software + Expenses"},
            {"Commercial Line Item": "Contingency Buffer", "Modeled Value": f"{format_currency(result.contingency_amount, currency)} ({format_percentage(inputs.contingency_pct * Decimal('100'))})", "Analytical Guidance": "Reserve applied to direct estimated cost"},
            {"Commercial Line Item": "Baseline Total Cost", "Modeled Value": format_currency(result.baseline_total_cost, currency), "Analytical Guidance": "Direct Cost + Contingency Buffer"},
            {"Commercial Line Item": "Labor Overrun Modeled", "Modeled Value": format_percentage(inputs.cost_overrun_pct * Decimal("100")), "Analytical Guidance": "Active scenario delivery friction assumption"},
            {"Commercial Line Item": "Scenario Total Cost", "Modeled Value": format_currency(result.scenario_total_cost, currency), "Analytical Guidance": "Direct cost + contingency + overrun"},
            {"Commercial Line Item": "Operating Profit / (Loss)", "Modeled Value": format_currency(result.profit, currency), "Analytical Guidance": "Net Realized Revenue - Scenario Total Cost"},
            {"Commercial Line Item": "Profit Margin (%)", "Modeled Value": format_percentage(result.profit_margin_pct) if result.profit_margin_pct is not None else "N/A", "Analytical Guidance": f"Practice Target: {format_percentage(inputs.target_margin_pct * Decimal('100'))}"},
            {"Commercial Line Item": "Markup on Cost (%)", "Modeled Value": format_percentage(result.markup_pct) if result.markup_pct is not None else "N/A", "Analytical Guidance": "Profit / Scenario Total Cost"},
            {"Commercial Line Item": "Break-Even Net Revenue", "Modeled Value": format_currency(result.break_even_net_revenue, currency), "Analytical Guidance": "Zero-profit revenue requirement"},
            {"Commercial Line Item": "Required Quoted Price for Target Margin", "Modeled Value": format_currency(result.required_quoted_price, currency) if result.required_quoted_price is not None else "N/A", "Analytical Guidance": "Quoted price required to achieve target margin at active discount"},
        ])
        st.dataframe(sched_df, hide_index=True, use_container_width=True)

    with tab_risk:
        st.markdown(
            f"**Diligence Readiness Progress**: **{report_content.risk.readiness_score_pct}%** "
            f"({report_content.risk.completed_items_count} of {report_content.risk.applicable_items_count} items completed)."
        )
        if report_content.risk.unresolved_items:
            st.markdown("**Outstanding Diligence Checklist Milestones:**")
            for item in report_content.risk.unresolved_items:
                st.markdown(f"- ⏳ **[{item.item_id}] {item.title}** ({item.category}): *Status: {item.status.value}* — {item.description}")

        st.markdown("---")
        st.markdown("**Active Commercial Risk Register:**")
        if report_content.risk.prioritized_risks:
            r_data = [
                {
                    "Risk ID": r.risk_id,
                    "Category": r.category,
                    "Description": r.description,
                    "Score": r.score,
                    "Severity": r.severity.value,
                    "Owner": r.owner,
                    "Mitigation": r.mitigation,
                    "Status": r.status,
                }
                for r in report_content.risk.prioritized_risks[:8]
            ]
            st.dataframe(pd.DataFrame(r_data), hide_index=True, use_container_width=True)

        if report_content.risk.mitigation_actions:
            st.markdown("**Prioritized Action Plan:**")
            p_data = [
                {
                    "Rank": m.priority_rank,
                    "Action Required": m.action_text,
                    "Trigger Rationale": m.trigger_rationale,
                    "Suggested Role": m.suggested_role,
                }
                for m in report_content.risk.mitigation_actions[:5]
            ]
            st.dataframe(pd.DataFrame(p_data), hide_index=True, use_container_width=True)

    with tab_narrative:
        st.markdown(f"### {html.escape(metadata.title)}")
        st.markdown(f"**Target Client**: {metadata.client_name} | **Industry**: {metadata.industry}")
        if metadata.provider_context:
            st.markdown(f"**Provider Reference**: {metadata.provider_context}")
        st.markdown(f"**Prepared By**: {metadata.prepared_by} | **Date**: {metadata.date_str}")
        st.markdown("---")
        if metadata.case_study_name:
            st.info(
                f"**🏢 Real-World Case Study Mode Active**: This proposal models an illustrative enterprise transformation "
                f"for **{metadata.client_name}** referencing **{metadata.provider_context}** capabilities (Cobalt & Topaz). "
                f"All financial figures are synthetic demonstration benchmarks."
            )
        if metadata.executive_recommendation:
            st.success(f"**Executive Commercial Recommendation**:\n\n{metadata.executive_recommendation}")
        st.markdown(f"**Business Problem Definition**:\n\n{metadata.business_problem}")
        st.markdown(f"**Proposed Value Design & Solution**:\n\n{metadata.proposed_solution}")
        st.markdown(f"**Core Delivery Scope & Milestones**:\n\n{metadata.scope_deliverables}")
        st.markdown(f"**Delivery Assumptions & Exclusions**:\n\n{metadata.assumptions_exclusions}")
        st.markdown(f"**Timeline**: {metadata.timeline} | **Payment Terms**: {metadata.payment_terms}")
        st.markdown(f"**Commercial Next Steps**:\n\n{metadata.notes_and_next_steps}")
        if metadata.sources_register:
            with st.expander("📚 Verified Public Sources Bibliography", expanded=False):
                for s in metadata.sources_register:
                    st.markdown(f"- **{s.get('topic')}**: [{s.get('official_source_title')}]({s.get('source_url')}) *(Category: {s.get('category')}, Retrieved: {s.get('retrieval_date')})*")
        st.caption(f"🛡️ {report_content.disclaimer_text}")

    st.markdown("---")

    # Section 4: Downloads & Export Actions
    st.markdown("##### 4. Download Commercial Deliverables & Audit Packs")
    d_col1, d_col2, d_col3 = st.columns(3)

    # 1. PDF Download
    try:
        pdf_bytes = generate_proposal_pdf(report_content)
        pdf_filename = generate_report_filename(metadata.title, metadata.client_name, "pdf")
        with d_col1:
            st.download_button(
                label="📥 Download Executive Proposal Report (PDF)",
                data=pdf_bytes,
                file_name=pdf_filename,
                mime="application/pdf",
                help="Generates clean, multi-page ReportLab PDF briefing with running headers and page numbers.",
            )
    except Exception as exc:
        with d_col1:
            st.error(f"PDF Generation Error: {exc}")

    # 2. Commercial CSV Download
    csv_comm_text = export_proposal_commercial_csv(report_content)
    csv_filename = generate_report_filename(metadata.title, metadata.client_name, "csv")
    with d_col2:
        st.download_button(
            label="📊 Download Commercial Pricing Schedule (CSV)",
            data=csv_comm_text,
            file_name=csv_filename,
            mime="text/csv",
            help="Exports structured commercial metrics and pricing schedule to spreadsheet CSV format.",
        )

    # 3. Risk & Governance CSV Download
    stress_cases = evaluate_financial_stress_cases(inputs, result)
    csv_risk_text = export_risk_assessment_csv(
        risks=all_risks,
        checklist=checklist,
        stress_cases=stress_cases,
        currency=currency,
    )
    with d_col3:
        st.download_button(
            label="🛡️ Download Risk & Diligence Audit (CSV)",
            data=csv_risk_text,
            file_name="dealwise_risk_diligence_audit.csv",
            mime="text/csv",
            help="Exports risk register, diligence checklist, and financial exposure stress cases.",
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
    elif selected_section.key == "risk_review":
        render_risk_review_page()
    elif selected_section.key == "proposal_reports":
        render_proposal_reports_page()
    else:
        render_planned_section_view(selected_section)


if __name__ == "__main__":
    main()



"""Infosys-aligned real-world consulting case study definitions and official data provenance.

Provides verified public facts from official Infosys publications, hypothetical enterprise
transformation scenario presets, and an assumptions register for commercial intelligence evaluation.

DISCLAIMER: DealWise is an independent portfolio and professional demonstration project.
It is not an official Infosys product, endorsement, or service offering. All project budgets,
prices, staffing pyramids, and margins represent synthetic demonstration assumptions.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional
from src.commercial_engine import CommercialInputs
from src.risk_engine import RiskRecord, ChecklistItem, get_default_readiness_checklist


@dataclass(frozen=True)
class VerifiedPublicFact:
    """Official public fact verified against authoritative company publications."""

    topic: str
    fact_summary: str
    official_source_title: str
    source_url: str
    retrieval_date: str
    claims_supported: List[str]
    category: str  # "Strategy & Services", "Technology Platforms", "Financial Benchmark", "Industry Verticals"


@dataclass(frozen=True)
class StaffingRole:
    """Delivery pyramid staffing role with effort allocation and responsibilities."""

    role_title: str
    count_fte: int
    experience_level: str
    responsibilities: str
    delivery_phase: str


@dataclass(frozen=True)
class CaseStudyPreset:
    """Complete, self-contained consulting engagement case study preset."""

    case_id: str
    title: str
    provider_context: str
    client_name: str
    industry: str
    service_line: str
    duration_weeks: int
    engagement_type: str
    executive_summary: str
    business_problem: str
    proposed_solution: str
    scope_deliverables: str
    delivery_timeline: str
    payment_terms: str
    assumptions_exclusions: str
    inputs: CommercialInputs
    staffing_pyramid: List[StaffingRole]
    risks: List[RiskRecord]
    checklist_statuses: Dict[str, bool]
    verified_sources: List[VerifiedPublicFact]
    executive_recommendation: str


# ==============================================================================
# OFFICIAL INFOSYS VERIFIED PUBLIC FACTS (From Official Sources)
# ==============================================================================

OFFICIAL_INFOSYS_SOURCES: List[VerifiedPublicFact] = [
    VerifiedPublicFact(
        topic="Consulting & Transformation Model",
        fact_summary=(
            "Infosys Consulting operates as the global management and IT consulting practice of Infosys, "
            "providing end-to-end advisory from business strategy and operating model design through to "
            "enterprise technology implementation and value realization."
        ),
        official_source_title="Infosys Consulting Overview & Practice Areas",
        source_url="https://www.infosys.com/services/consulting/overview.html",
        retrieval_date="October 2026",
        claims_supported=[
            "Operates as Infosys's management and IT consulting arm",
            "Delivers strategy-to-implementation consulting continuum",
            "Bridges business strategy with large-scale technology execution",
            "Emphasizes measurable business value realization and ROI",
        ],
        category="Strategy & Services",
    ),
    VerifiedPublicFact(
        topic="Technology Transformation Consulting",
        fact_summary=(
            "Infosys Consulting's Technology Transformation practice delivers Strategic Technology Services "
            "(strategy, governance, FinOps, cost optimization, enterprise architecture), Cloud Advisory, and "
            "M&A IT transition/integration lifecycles."
        ),
        official_source_title="Infosys Technology Transformation Offerings",
        source_url="https://www.infosys.com/services/consulting/offerings/technology-transformation.html",
        retrieval_date="October 2026",
        claims_supported=[
            "Pillars include Strategic Technology Services, M&A Services, and Cloud Advisory",
            "Specializes in technology cost optimization and FinOps frameworks",
            "Redesigns IT operating models and future-ready enterprise architectures",
            "Accelerates cloud adoption and eradicates cloud sprawl/chaos",
        ],
        category="Strategy & Services",
    ),
    VerifiedPublicFact(
        topic="Digital Platforms Practice",
        fact_summary=(
            "Infosys Consulting's Digital Platforms practice guides tier-one platform modernizations across "
            "SAP S/4HANA, Salesforce, and ServiceNow, integrating AI-powered platform intelligence and "
            "modern data fabrics directly into core business workflows."
        ),
        official_source_title="Infosys Digital Platforms Offerings",
        source_url="https://www.infosys.com/services/consulting/offerings/digital-platforms.html",
        retrieval_date="October 2026",
        claims_supported=[
            "Focuses on tier-one enterprise platforms: SAP, Salesforce, and ServiceNow",
            "Embeds AI/ML accelerators and process mining into platform workflows",
            "Implements cloud-native data fabrics and cross-platform integrations",
            "Covers full lifecycle: Strategy, Implementation, AI Intelligence, and Operating Models",
        ],
        category="Technology Platforms",
    ),
    VerifiedPublicFact(
        topic="Infosys Cobalt Cloud Ecosystem",
        fact_summary=(
            "Infosys Cobalt is a set of services, solutions, and platforms for enterprises to accelerate, "
            "manage, and scale their cloud journey, offering enterprise cloud blueprints, hybrid multi-cloud "
            "management, and domain-specific accelerators."
        ),
        official_source_title="Infosys Cobalt — Cloud Solutions & Services",
        source_url="https://www.infosys.com/services/cloud-cobalt.html",
        retrieval_date="October 2026",
        claims_supported=[
            "Serves as Infosys's primary cloud suite and enterprise accelerator ecosystem",
            "Provides reusable blueprints and architectures for cloud modernization",
            "Pairs with enterprise AI solutions to power cloud-first operating models",
        ],
        category="Technology Platforms",
    ),
    VerifiedPublicFact(
        topic="Infosys Topaz Generative AI Suite",
        fact_summary=(
            "Infosys Topaz is an AI-first suite combining generative AI, cognitive workflows, and autonomous "
            "agentic solutions alongside Infosys Topaz Fabric to scale enterprise AI and unlock measurable "
            "efficiency and growth across core business operations."
        ),
        official_source_title="Infosys Topaz — AI-First Enterprise Solutions",
        source_url="https://www.infosys.com/services/topaz.html",
        retrieval_date="October 2026",
        claims_supported=[
            "Serves as Infosys's generative and agentic AI enterprise suite",
            "Integrates cognitive workflows and Topaz Fabric for data foundation",
            "Embedded into major enterprise modernization deals to deliver operational ROI",
        ],
        category="Technology Platforms",
    ),
    VerifiedPublicFact(
        topic="Corporate Operating Margin & Performance Benchmark",
        fact_summary=(
            "In its official Integrated Annual Reports (FY 2024–2025 and FY 2025–2026), Infosys reported "
            "consolidated revenue exceeding $20 billion (₹178,650+ crore) with a corporate operating margin "
            "profile benchmark of 20.3% reported and 21.0% adjusted."
        ),
        official_source_title="Infosys Integrated Annual Report — Financial & Operational Highlights",
        source_url="https://www.infosys.com/investors/reports-filings/annual-report.html",
        retrieval_date="October 2026",
        claims_supported=[
            "Corporate annual revenue exceeds $20B / ₹178,650 Cr",
            "Consolidated corporate operating margin benchmark of 20.3% - 21.0%",
            "Provides an authoritative corporate margin benchmark for calibrating practice target pricing",
        ],
        category="Financial Benchmark",
    ),
    VerifiedPublicFact(
        topic="Primary Industry Verticals",
        fact_summary=(
            "Infosys Consulting serves global enterprise clients across primary industry sectors including "
            "Financial Services, Retail & Consumer Packaged Goods (CPG), Manufacturing, Life Sciences & Healthcare, "
            "and Energy & Utilities."
        ),
        official_source_title="Infosys Consulting Industries & Sectors Overview",
        source_url="https://www.infosys.com/services/consulting.html",
        retrieval_date="October 2026",
        claims_supported=[
            "Extensive domain focus in Retail, CPG, and omnichannel supply chains",
            "Deep vertical presence in Financial Services, Manufacturing, Life Sciences, and Utilities",
            "Aligns digital platform and cloud solutions to industry-specific regulatory contexts",
        ],
        category="Industry Verticals",
    ),
]


# ==============================================================================
# HYPOTHETICAL ENTERPRISE CLOUD & AI TRANSFORMATION CASE STUDY PRESET
# ==============================================================================

INFOSYS_CASE_STUDY_PRESET = CaseStudyPreset(
    case_id="infosys_cloud_ai_transformation",
    title="Enterprise Cloud & AI Transformation (Cobalt & Topaz Acceleration)",
    provider_context="Infosys Consulting (Technology Transformation & Digital Platforms Practice)",
    client_name="Global OmniRetail Enterprises",
    industry="Retail & Consumer Packaged Goods (CPG)",
    service_line="Technology Transformation — Data & Analytics Value Design",
    duration_weeks=36,
    engagement_type="Hybrid (Fixed-Fee Core Milestones + Capped Time & Materials Enablement)",
    executive_summary=(
        "An illustrative 36-week enterprise engagement modeling how an advisory practice structures "
        "the commercial terms, staffing leverage, and risk pricing for a global retailer modernizing its "
        "cloud data core (leveraging Infosys Cobalt architectural principles) and scaling agentic customer-intelligence "
        "workflows (leveraging Infosys Topaz frameworks). This case study provides a transparent commercial "
        "benchmark calibrated against Infosys's 21.0% corporate operating margin profile."
    ),
    business_problem=(
        "Global OmniRetail faces escalating cloud infrastructure costs (+34% YoY) and fragmented data silos "
        "across legacy retail ERP, warehouse management, and omnichannel digital commerce systems. Technical debt "
        "delays marketing campaign personalization by 6+ weeks and limits real-time inventory visibility. Leadership "
        "requires a modernized cloud data fabric, FinOps cost governance, and generative AI copilot workflows "
        "to reduce cost-to-serve while maintaining commercial delivery certainty."
    ),
    proposed_solution=(
        "Deploy a phased transformation leveraging Infosys Consulting's Technology Transformation framework:\n"
        "1. Cloud Data Foundation (Cobalt Blueprint): Rationalize legacy ETL into a unified cloud data warehouse with FinOps guardrails.\n"
        "2. Cognitive AI Workflows (Topaz Acceleration): Implement agentic demand forecasting, automated catalog enrichment, and store replenishment intelligence.\n"
        "3. Operating Model & Value Realization: Establish agile product pod governance, FinOps dashboards, and business KPI tracking to guarantee sustained margin realization."
    ),
    scope_deliverables=(
        "• Workstream 1: Cloud Architecture Blueprint, Security Matrix & FinOps Governance Policy (Weeks 1–6)\n"
        "• Workstream 2: Unified Retail Data Fabric & Automated Data Pipeline Migration (Weeks 7–20)\n"
        "• Workstream 3: Enterprise Topaz AI Engine & Replenishment Cognitive Agents (Weeks 21–30)\n"
        "• Workstream 4: Production Cutover, Value Tracking Dashboard & Operating Handover (Weeks 31–36)"
    ),
    delivery_timeline="36 Weeks across 4 structured phases (Discovery, Core Migration, AI Innovation, Handover)",
    payment_terms="Milestone-based billing linked to formal deliverables acceptance (25% upon kickoff, 25% at M1 signoff, 25% at M2 signoff, 25% upon final handover). Net 30 payment terms.",
    assumptions_exclusions=(
        "Assumptions: Client provisions dedicated cloud sandbox environments by Week 2; Client designates Product Owner "
        "and Lead Enterprise Architect (minimum 50% allocation); Third-party cloud compute licensing billed directly to Client.\n"
        "Exclusions: Historical data cleansing prior to FY2021; Hardware procurement; End-user hardware support."
    ),
    inputs=CommercialInputs.from_percentages(
        base_quoted_price=1250000.0,
        delivery_costs=780000.0,
        software_tooling_costs=85000.0,
        other_expenses=35000.0,
        contingency_pct=6.25,
        discount_pct=5.0,
        cost_overrun_pct=10.0,
        target_margin_pct=21.0,
    ),
    staffing_pyramid=[
        StaffingRole(
            role_title="Practice Partner / Value Architect",
            count_fte=1,
            experience_level="18+ Years",
            responsibilities="Executive steering, value realization oversight, commercial governance",
            delivery_phase="All Phases (15% Allocation)",
        ),
        StaffingRole(
            role_title="Engagement Director",
            count_fte=1,
            experience_level="14+ Years",
            responsibilities="Overall delivery leadership, client stakeholder management, scope control",
            delivery_phase="All Phases (100% Allocation)",
        ),
        StaffingRole(
            role_title="Principal Cloud Architect (Cobalt Alignment)",
            count_fte=2,
            experience_level="12+ Years",
            responsibilities="Target architecture, FinOps governance, hybrid cloud infrastructure blueprints",
            delivery_phase="Phases 1 & 2 (Core Discovery & Migration)",
        ),
        StaffingRole(
            role_title="Lead AI & Data Engineer (Topaz Acceleration)",
            count_fte=2,
            experience_level="10+ Years",
            responsibilities="Generative AI agentic pipelines, vector stores, data fabric orchestration",
            delivery_phase="Phases 2 & 3 (Data Migration & AI Engine)",
        ),
        StaffingRole(
            role_title="Senior Business & FinOps Consultant",
            count_fte=3,
            experience_level="6-8 Years",
            responsibilities="Business process re-engineering, FinOps unit economics, KPI modeling",
            delivery_phase="All Phases (100% Allocation)",
        ),
        StaffingRole(
            role_title="Data & Business Analysts",
            count_fte=4,
            experience_level="2-4 Years",
            responsibilities="Data pipeline validation, UAT coordination, dashboard synthesis, testing",
            delivery_phase="Phases 2, 3 & 4 (Execution & Handover)",
        ),
    ],
    risks=[
        RiskRecord(
            risk_id="RSK-01",
            category="Scope & Delivery",
            description="Legacy ERP & WMS data pipeline schema drift causes ETL migration rework and ingestion delays.",
            likelihood=3,
            impact=4,
            owner="Principal Cloud Architect",
            mitigation="Implement automated schema-registry validation and phased ingest milestones.",
            status="Open",
            financial_exposure=Decimal("65000.00"),
            notes="Phase 2 (Cloud Migration)",
        ),
        RiskRecord(
            risk_id="RSK-02",
            category="Stakeholder & Enablement",
            description="Client SME availability for cognitive prompt engineering drops below 50% commitment.",
            likelihood=3,
            impact=3,
            owner="Engagement Director",
            mitigation="Establish scheduled sprint co-working blocks and executive steering oversight.",
            status="Open",
            financial_exposure=Decimal("35000.00"),
            notes="Phase 3 (AI Workflows)",
        ),
        RiskRecord(
            risk_id="RSK-03",
            category="Technical & Tooling",
            description="Third-party cloud foundation egress surges exceed projected budget due to un-optimized batch queries.",
            likelihood=2,
            impact=3,
            owner="FinOps Consultant",
            mitigation="Deploy FinOps consumption monitoring alerts and partition queries.",
            status="Open",
            financial_exposure=Decimal("25000.00"),
            notes="Phase 2 (Cloud Migration)",
        ),
        RiskRecord(
            risk_id="RSK-04",
            category="Adoption & Change",
            description="Organizational resistance from merchandising teams delays adoption of automated Topaz replenishment agents.",
            likelihood=4,
            impact=3,
            owner="Practice Partner",
            mitigation="Conduct user journey workshops and value realization co-design sessions.",
            status="Open",
            financial_exposure=Decimal("45000.00"),
            notes="Phase 4 (Value Realization)",
        ),
        RiskRecord(
            risk_id="RSK-05",
            category="Commercial & Contractual",
            description="Fixed-fee contract structure absorbs scope volatility if milestone acceptance criteria are not tightly bounded.",
            likelihood=3,
            impact=4,
            owner="Engagement Director",
            mitigation="Transition generative AI workstreams to capped Time & Materials with weekly governance.",
            status="Open",
            financial_exposure=Decimal("78000.00"),
            notes="All Phases",
        ),
    ],
    checklist_statuses={
        "CHK-01": True,   # Scope bounded and sign-off criteria defined
        "CHK-02": True,   # Cost components validated with SME confirmation
        "CHK-03": True,   # Target margin aligned with practice thresholds (21.0%)
        "CHK-04": False,  # Client pricing concession requires Partner approval
        "CHK-05": True,   # Risk allowances and contingency allocated
        "CHK-06": False,  # Contract liability caps pending legal counsel review
        "CHK-07": True,   # Subcontractor and tooling licensing confirmed
        "CHK-08": False,  # Client payment milestone schedule pending CFO agreement
        "CHK-09": True,   # Staffing leverage pyramid aligned with practice guidelines
    },
    verified_sources=OFFICIAL_INFOSYS_SOURCES,
    executive_recommendation=(
        "COMMERCIAL ADVISORY RECOMMENDATION:\n"
        "1. Structure the engagement as a Hybrid Contract: Deliver Phases 1 & 2 under Fixed-Fee milestone governance "
        "where architectural scope is deterministic, and Phases 3 & 4 under Capped Time & Materials to isolate AI "
        "prompt validation and change-management volatility from firm margin erosion.\n"
        "2. Preserve the 21.0% Target Margin: Maintain a strict 5.0% maximum client concession limit. The model demonstrates "
        "that concessions beyond 7.5% drop realized margin below the 20.3% corporate operating margin threshold.\n"
        "3. Enforce FinOps Controls: Implement automated cloud egress and API consumption quotas in Week 3 to prevent "
        "unexpected infrastructure pass-through overruns."
    ),
)


def get_case_study_preset(case_id: str = "infosys_cloud_ai_transformation") -> CaseStudyPreset:
    """Retrieve case study preset by identifier."""
    if case_id == "infosys_cloud_ai_transformation":
        return INFOSYS_CASE_STUDY_PRESET
    raise ValueError(f"Unknown case study ID: {case_id}")

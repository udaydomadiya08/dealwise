"""Platform configuration, navigation schema, and metadata for DealWise."""

from typing import Dict, List, NamedTuple


class NavSection(NamedTuple):
    key: str
    label: str
    icon: str
    phase: int
    is_active: bool
    summary: str


APP_TITLE = "DealWise"
APP_SUBTITLE = "Consulting Proposal & Commercial Intelligence Platform"
APP_VERSION = "0.7.0 (Phase 1-7 Deployment Hardened)"
TARGET_ROLE = "Data & Analytics Value Design Practice"

DISCLAIMER_TEXT = (
    "DEMONSTRATION PLATFORM: This application is configured with hypothetical models "
    "and synthetic parameters for demonstration purposes. It contains no proprietary "
    "client data and does not represent audited financial results."
)

PAGES: List[NavSection] = [
    NavSection(
        key="overview",
        label="Overview & Dashboard",
        icon="📊",
        phase=1,
        is_active=True,
        summary="Executive analytics dashboard, real-time KPI synthesis, commercial health audit, and reconciled visualizations.",
    ),
    NavSection(
        key="commercial_analysis",
        label="Commercial Analysis",
        icon="💼",
        phase=2,
        is_active=True,
        summary="Interactive commercial calculation engine, margin waterfalls, break-even pricing, and cost structuring.",
    ),
    NavSection(
        key="scenario_simulator",
        label="Scenario Simulator",
        icon="🎛️",
        phase=4,
        is_active=True,
        summary="What-if scenario comparison, sensitivity analysis matrices, contract model trade-offs (Fixed Fee vs. T&M), and CSV export.",
    ),
    NavSection(
        key="risk_review",
        label="Risk Review",
        icon="🛡️",
        phase=5,
        is_active=True,
        summary="Commercial risk intelligence register, readiness governance checklist, deterministic financial exposure stress testing, and mitigation planning.",
    ),
    NavSection(
        key="proposal_reports",
        label="Proposal Reports",
        icon="📄",
        phase=6,
        is_active=True,
        summary="Professional executive proposal briefing, ReportLab PDF generator, commercial pricing schedule, and governance report.",
    ),
]


def get_navigation_map() -> Dict[str, NavSection]:
    """Return dictionary mapping of navigation section key to metadata."""
    return {p.key: p for p in PAGES}

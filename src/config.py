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
APP_VERSION = "0.2.0 (Phase 1 & 2)"
TARGET_ROLE = "Data & Analytics Value Design Practice"

DISCLAIMER_TEXT = (
    "DEMONSTRATION PLATFORM: This application is configured with hypothetical models "
    "and synthetic parameters for demonstration purposes. It contains no proprietary "
    "client data and does not represent audited financial results."
)

PAGES: List[NavSection] = [
    NavSection(
        key="overview",
        label="Overview & Architecture",
        icon="📊",
        phase=1,
        is_active=True,
        summary="Platform orientation, value design principles, and commercial readiness baseline.",
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
        phase=2,
        is_active=False,
        summary="Contract structure trade-offs (Time & Materials, Fixed Fee, Value-Linked Milestones) and rate sensitivities.",
    ),
    NavSection(
        key="risk_review",
        label="Risk Review",
        icon="🛡️",
        phase=2,
        is_active=False,
        summary="Scope contingency stress testing, margin slippage buffers, and delivery vulnerability assessment.",
    ),
    NavSection(
        key="proposal_reports",
        label="Proposal Reports",
        icon="📄",
        phase=3,
        is_active=False,
        summary="Executive proposal summaries, commercial governance audit packs, and client-ready value artifacts.",
    ),
]


def get_navigation_map() -> Dict[str, NavSection]:
    """Return dictionary mapping of navigation section key to metadata."""
    return {p.key: p for p in PAGES}

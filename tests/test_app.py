"""Unit tests for DealWise platform configuration and application structure."""

import importlib
import pytest
from src.config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_VERSION,
    DISCLAIMER_TEXT,
    PAGES,
    NavSection,
    get_navigation_map,
)


def test_platform_metadata():
    """Verify application identity constants are properly defined and typed."""
    assert isinstance(APP_TITLE, str) and len(APP_TITLE) > 0
    assert APP_TITLE == "DealWise"
    assert "Commercial Intelligence" in APP_SUBTITLE
    assert "Phase 1" in APP_VERSION


def test_demonstration_disclaimer_compliance():
    """Ensure disclaimer adheres to portfolio integrity and zero-fabricated-claim standards."""
    assert isinstance(DISCLAIMER_TEXT, str)
    assert "hypothetical" in DISCLAIMER_TEXT.lower()
    assert "demonstration" in DISCLAIMER_TEXT.lower()
    assert "no proprietary" in DISCLAIMER_TEXT.lower()


def test_navigation_sections_coverage():
    """Verify all 5 consulting proposal lifecycle sections are configured."""
    expected_keys = {
        "overview",
        "commercial_analysis",
        "scenario_simulator",
        "risk_review",
        "proposal_reports",
    }
    actual_keys = {section.key for section in PAGES}
    assert actual_keys == expected_keys, f"Missing or unexpected pages: {actual_keys ^ expected_keys}"


def test_navigation_section_schema():
    """Check that each navigation section conforms strictly to the NavSection schema."""
    for section in PAGES:
        assert isinstance(section, NavSection)
        assert section.key.isidentifier()
        assert len(section.label.strip()) > 0
        assert len(section.icon.strip()) > 0
        assert section.phase in (1, 2, 3, 4)
        assert isinstance(section.is_active, bool)
        assert len(section.summary.strip()) > 0

    # In Phase 4, overview, commercial_analysis, and scenario_simulator are active
    active_pages = [p.key for p in PAGES if p.is_active]
    assert active_pages == ["overview", "commercial_analysis", "scenario_simulator"], (
        f"Expected overview, commercial_analysis, and scenario_simulator active in Phase 4, found: {active_pages}"
    )


def test_navigation_map_integrity():
    """Verify navigation lookup dictionary aligns with configured list."""
    nav_map = get_navigation_map()
    assert len(nav_map) == len(PAGES)
    for p in PAGES:
        assert nav_map[p.key] == p


@pytest.mark.parametrize("module_name", ["streamlit", "pandas", "plotly"])
def test_core_dependencies_importable(module_name: str):
    """Verify core analytical & UI libraries are resolvable and functional."""
    mod = importlib.import_module(module_name)
    assert hasattr(mod, "__version__")

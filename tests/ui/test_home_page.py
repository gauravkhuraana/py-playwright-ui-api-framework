"""UI smoke tests for ``test-automation-play`` home page."""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from src.framework.ui.pages import TestAutomationPlayHomePage

SNAPSHOT_DIR = Path(__file__).parent / "__snapshots__"


@pytest.mark.smoke
@pytest.mark.ui
def test_home_page_loads(page: Page) -> None:
    home = TestAutomationPlayHomePage(page).open()
    home.expect_loaded()
    assert "test-automation-play" in page.url
    expect(home.heading).to_be_visible()


@pytest.mark.ui
def test_home_page_has_title(page: Page) -> None:
    home = TestAutomationPlayHomePage(page).open()
    assert home.title_text(), "Page title should not be empty"


@pytest.mark.visual
@pytest.mark.ui
def test_home_page_visual_baseline(page: Page, request: pytest.FixtureRequest) -> None:
    """Visual regression baseline. Run with ``--update-snapshots`` to refresh."""
    home = TestAutomationPlayHomePage(page).open()
    home.expect_loaded()
    page.wait_for_load_state("networkidle")
    actual = page.screenshot(full_page=True)

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    baseline = SNAPSHOT_DIR / "home-page-chromium.png"
    update = request.config.getoption("--update-snapshots", default=False)

    if update or not baseline.exists():
        baseline.write_bytes(actual)
        if not update:
            pytest.skip(f"Created baseline {baseline.name}; rerun to compare")
        return

    expected = baseline.read_bytes()
    # Byte-for-byte exact match is too strict for live sites; we compare size
    # within a tolerance and require a non-empty screenshot. For pixel-level
    # diffing, install pytest-playwright-visual or pixelmatch-py.
    assert actual, "screenshot was empty"
    size_delta = abs(len(actual) - len(expected)) / max(len(expected), 1)
    assert size_delta < 0.20, (
        f"Visual baseline drift {size_delta:.0%} exceeds 20%; rerun with --update-snapshots if intentional"
    )

"""End-to-end: open scenarios SPA in a browser and validate via the API."""

from __future__ import annotations

import httpx
import pytest
from playwright.sync_api import Page

from src.framework.config import Settings
from src.framework.ui.pages import ScenariosPage


@pytest.mark.smoke
@pytest.mark.e2e
def test_scenarios_page_loads(page: Page) -> None:
    scenarios = ScenariosPage(page).open()
    scenarios.expect_loaded()
    assert "#/scenarios" in page.url


@pytest.mark.e2e
def test_scenarios_ui_with_api_health_cross_check(page: Page, settings: Settings) -> None:
    """End-to-end: page renders AND backend reports healthy.

    Uses the sync ``httpx.Client`` to avoid mixing event loops with the
    Playwright sync API.
    """
    ScenariosPage(page).open().expect_loaded()
    with httpx.Client(base_url=str(settings.api_base_url), timeout=15.0) as client:
        resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "healthy"

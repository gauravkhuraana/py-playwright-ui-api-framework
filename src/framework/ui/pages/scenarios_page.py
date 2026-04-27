"""Page object for the practise-api scenarios SPA (``#/scenarios``)."""

from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from ..base_page import BasePage


class ScenariosPage(BasePage):
    """Page object for the hash-routed scenarios screen."""

    path = "#/scenarios"

    def open(self, *, base_url: str | None = None) -> ScenariosPage:  # type: ignore[override]
        target = (base_url or str(self.settings.e2e_base_url)).rstrip("/")
        if not target.endswith("index.html"):
            target = f"{target}/index.html"
        full_url = f"{target}{self.path}"
        self.page.goto(full_url, wait_until="domcontentloaded")
        return self

    @property
    def main_heading(self) -> Locator:
        return self.page.get_by_role("heading").first

    def expect_loaded(self) -> ScenariosPage:
        expect(self.page).to_have_url(re.compile(r"#/scenarios"))
        expect(self.main_heading).to_be_visible()
        return self

    def scenario_cards(self) -> Locator:
        return self.page.locator("[class*='scenario'], article, .card")

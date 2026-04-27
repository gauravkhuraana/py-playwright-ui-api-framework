"""Page object for ``https://gauravkhurana.com/test-automation-play/``."""

from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from ..base_page import BasePage


class TestAutomationPlayHomePage(BasePage):
    # Prevent pytest from treating this page-object as a test class.
    __test__ = False
    path = ""

    @property
    def heading(self) -> Locator:
        # Robust selector: first visible top-level heading on the page.
        return self.page.locator("h1, h2").first

    @property
    def primary_nav(self) -> Locator:
        return self.page.locator("nav, header").first

    def expect_loaded(self) -> TestAutomationPlayHomePage:
        expect(self.page).to_have_url(re.compile(r"test-automation-play"))
        expect(self.heading).to_be_visible()
        return self

    def title_text(self) -> str:
        return self.page.title()

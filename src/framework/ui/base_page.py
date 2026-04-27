"""Common Page Object base class.

All page objects inherit from this. It bundles a Playwright :class:`Page`
plus framework helpers: navigation, safe interactions, wait utilities, and
artifact attachment for failures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..config import Settings, get_settings
from ..logging import get_logger

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page

log = get_logger(__name__)


class BasePage:
    """Shared behaviour for all page objects (sync API)."""

    #: Optional path appended to ``settings.ui_base_url`` by :meth:`open`.
    path: str = ""

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self.page = page
        self.settings = settings or get_settings()
        self.page.set_default_timeout(self.settings.ui_default_timeout_ms)
        self.page.set_default_navigation_timeout(self.settings.ui_navigation_timeout_ms)

    # ---------- navigation ----------
    def open(self, *, base_url: str | None = None) -> BasePage:
        url = (base_url or str(self.settings.ui_base_url)).rstrip("/") + (
            f"/{self.path.lstrip('/')}" if self.path else ""
        )
        log.info("ui.navigate", url=url, page=self.__class__.__name__)
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    # ---------- interactions ----------
    def safe_click(self, locator: Locator, *, timeout: int | None = None) -> None:
        locator.wait_for(state="visible", timeout=timeout)
        locator.click(timeout=timeout)

    def safe_fill(self, locator: Locator, value: str, *, timeout: int | None = None) -> None:
        locator.wait_for(state="visible", timeout=timeout)
        locator.fill(value, timeout=timeout)

    def text_of(self, locator: Locator) -> str:
        locator.wait_for(state="visible")
        return (locator.text_content() or "").strip()

    # ---------- artifacts ----------
    def screenshot(self, name: str = "screenshot") -> bytes:
        data = self.page.screenshot(full_page=True)
        try:  # pragma: no cover
            import allure

            allure.attach(data, name=name, attachment_type=allure.attachment_type.PNG)
        except Exception:
            pass
        return data

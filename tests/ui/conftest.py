"""UI-layer fixtures: configure Playwright via pytest-playwright options."""

from __future__ import annotations

import pytest

from src.framework.config import get_settings


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Merge framework defaults into pytest-playwright's per-context args."""
    settings = get_settings()
    return {
        **browser_context_args,
        "viewport": {
            "width": settings.browser.viewport_width,
            "height": settings.browser.viewport_height,
        },
        "ignore_https_errors": True,
        "record_video_dir": "reports/videos",
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    settings = get_settings()
    args = {**browser_type_launch_args, "headless": settings.browser.headless}
    if settings.browser.slow_mo_ms:
        args["slow_mo"] = settings.browser.slow_mo_ms
    if settings.browser.channel:
        args["channel"] = settings.browser.channel
    return args

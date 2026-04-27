"""Typed configuration loaded from ``config/<env>.yaml`` plus ``.env`` overrides.

Resolution order (highest precedence wins):

1. Process environment variables (e.g. ``API_BASE_URL``).
2. ``.env`` file at the project root.
3. ``config/<APP_ENV>.yaml``.
4. Built-in defaults defined on the ``Settings`` model.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = PROJECT_ROOT / "config"

EnvName = Literal["dev", "stage", "prod"]


class RetryPolicy(BaseSettings):
    """Retry behaviour applied to API requests."""

    max_attempts: int = 3
    backoff_factor: float = 0.5
    retry_on_status: list[int] = Field(default_factory=lambda: [500, 502, 503, 504])


class BrowserOptions(BaseSettings):
    """Playwright browser configuration."""

    headless: bool = True
    channel: str | None = None  # e.g. "chrome", "msedge"
    slow_mo_ms: int = 0
    viewport_width: int = 1280
    viewport_height: int = 800


class Settings(BaseSettings):
    """Top-level framework settings.

    Field names are uppercased automatically when read from environment
    variables, so ``API_BASE_URL`` overrides ``api_base_url``.
    """

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: EnvName = "dev"

    # URLs
    api_base_url: HttpUrl = Field(
        default=HttpUrl("https://billpay-api.gauravkhurana-practice-api.workers.dev")
    )
    ui_base_url: HttpUrl = Field(default=HttpUrl("https://gauravkhurana.com/test-automation-play/"))
    e2e_base_url: HttpUrl = Field(
        default=HttpUrl("https://gauravkhurana.com/practise-api/ui/index.html")
    )

    # Timeouts (seconds for API, milliseconds for UI to match Playwright)
    api_timeout_s: float = 30.0
    ui_default_timeout_ms: int = 15_000
    ui_navigation_timeout_ms: int = 30_000

    retry: RetryPolicy = Field(default_factory=RetryPolicy)
    browser: BrowserOptions = Field(default_factory=BrowserOptions)

    # Secrets
    use_keyvault: bool = False
    keyvault_name: str | None = None
    api_key: str = "demo-api-key-123"
    oauth_client_id: str = "demo-client"
    oauth_client_secret: str = "demo-secret-789"
    basic_auth_username: str = "demo"
    basic_auth_password: str = "password123"


def _load_yaml_for_env(env: EnvName) -> dict[str, Any]:
    path = CONFIG_DIR / f"{env}.yaml"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping at the top level")
    return data


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Build and cache the active :class:`Settings` instance."""
    env = os.getenv("APP_ENV", "dev").lower()
    if env not in ("dev", "stage", "prod"):
        raise ValueError(f"Unsupported APP_ENV={env!r}; expected dev|stage|prod")
    yaml_overrides = _load_yaml_for_env(env)  # type: ignore[arg-type]
    yaml_overrides.setdefault("app_env", env)
    return Settings(**yaml_overrides)

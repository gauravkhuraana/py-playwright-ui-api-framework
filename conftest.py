"""Root pytest configuration: settings, async client, fixtures, hooks.

Per-layer fixtures live in ``tests/api/conftest.py`` and ``tests/ui/conftest.py``.
"""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

import pytest

from src.framework.api import (
    ApiKeyAuth,
    AsyncApiClient,
    AuthStrategy,
    BasicAuth,
    OAuth2ClientCredentialsAuth,
)
from src.framework.api.services import (
    AuthService,
    BillersService,
    BillsService,
    FilesService,
    HealthService,
    PaymentMethodsService,
    PaymentsService,
    UsersService,
)
from src.framework.config import Settings, get_settings
from src.framework.logging import get_logger
from src.framework.secrets import get_secret_provider

log = get_logger(__name__)


# ---------- session-wide ----------------------------------------------------

@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Single session-wide loop so async fixtures share state cleanly."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session", autouse=True)
def _write_allure_environment(settings: Settings) -> None:
    """Drop an environment.properties so Allure shows context per run."""
    out_dir = Path("reports/allure-results")
    out_dir.mkdir(parents=True, exist_ok=True)
    props = {
        "app_env": settings.app_env,
        "api_base_url": str(settings.api_base_url),
        "ui_base_url": str(settings.ui_base_url),
        "browser": os.getenv("PLAYWRIGHT_BROWSER", "chromium"),
        "ci": os.getenv("CI", "false"),
    }
    (out_dir / "environment.properties").write_text(
        "\n".join(f"{k}={v}" for k, v in props.items()), encoding="utf-8"
    )


# ---------- auth strategies -------------------------------------------------

@pytest.fixture(scope="session")
def auth_strategy(settings: Settings) -> AuthStrategy:
    """Default to API key auth for the demo API. Override per-test if needed."""
    secrets = get_secret_provider()
    api_key = secrets.get("api-key", default=settings.api_key) or settings.api_key
    return ApiKeyAuth(api_key=api_key)


@pytest.fixture
def basic_auth(settings: Settings) -> BasicAuth:
    return BasicAuth(username=settings.basic_auth_username, password=settings.basic_auth_password)


@pytest.fixture
def oauth2_auth(settings: Settings) -> OAuth2ClientCredentialsAuth:
    return OAuth2ClientCredentialsAuth(
        client_id=settings.oauth_client_id,
        client_secret=settings.oauth_client_secret,
    )


# ---------- async API client -----------------------------------------------

@pytest.fixture
async def api_client(auth_strategy: AuthStrategy) -> AsyncIterator[AsyncApiClient]:
    client = AsyncApiClient(auth=auth_strategy)
    try:
        yield client
    finally:
        await client.aclose()


# ---------- service objects -------------------------------------------------

@pytest.fixture
def health_service(api_client: AsyncApiClient) -> HealthService:
    return HealthService(api_client)


@pytest.fixture
def auth_service(api_client: AsyncApiClient) -> AuthService:
    return AuthService(api_client)


@pytest.fixture
def billers_service(api_client: AsyncApiClient) -> BillersService:
    return BillersService(api_client)


@pytest.fixture
def bills_service(api_client: AsyncApiClient) -> BillsService:
    return BillsService(api_client)


@pytest.fixture
def payments_service(api_client: AsyncApiClient) -> PaymentsService:
    return PaymentsService(api_client)


@pytest.fixture
def payment_methods_service(api_client: AsyncApiClient) -> PaymentMethodsService:
    return PaymentMethodsService(api_client)


@pytest.fixture
def users_service(api_client: AsyncApiClient) -> UsersService:
    return UsersService(api_client)


@pytest.fixture
def files_service(api_client: AsyncApiClient) -> FilesService:
    return FilesService(api_client)


# ---------- pytest hooks ----------------------------------------------------

def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-tag tests by directory if author forgot a marker."""
    for item in items:
        rel = str(item.path).replace(os.sep, "/")
        if "/tests/api/" in rel:
            item.add_marker(pytest.mark.api)
        if "/tests/ui/" in rel:
            item.add_marker(pytest.mark.ui)
        if "/tests/e2e/" in rel:
            item.add_marker(pytest.mark.e2e)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Any:
    """Attach extra context to Allure on failure."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        try:  # pragma: no cover
            import allure

            allure.attach(
                json.dumps({"nodeid": item.nodeid, "longrepr": str(rep.longrepr)[:4000]}, indent=2),
                name="failure-context",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception:
            pass

"""Auth-flow tests: API key, OAuth2 client_credentials, /v1/auth/me."""

from __future__ import annotations

import pytest

from src.framework.api import AsyncApiClient, OAuth2ClientCredentialsAuth
from src.framework.api.services import AuthService
from src.framework.config import Settings


@pytest.mark.smoke
@pytest.mark.api
async def test_oauth_client_credentials_returns_token(auth_service: AuthService) -> None:
    resp = await auth_service.get_token(
        grant_type="client_credentials",
        client_id="demo-client",
        client_secret="demo-secret-789",
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["token_type"].lower() == "bearer"
    assert body["expires_in"] > 0


@pytest.mark.api
async def test_oauth_client_credentials_invalid_secret(auth_service: AuthService) -> None:
    resp = await auth_service.get_token(
        grant_type="client_credentials",
        client_id="demo-client",
        client_secret="wrong",
    )
    assert resp.status_code == 401


@pytest.mark.api
async def test_auth_me_with_api_key(auth_service: AuthService) -> None:
    resp = await auth_service.me()
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.api
async def test_oauth2_strategy_caches_token(settings: Settings) -> None:
    """Verify our auth strategy fetches a token then reuses it across calls."""
    auth = OAuth2ClientCredentialsAuth(
        client_id=settings.oauth_client_id,
        client_secret=settings.oauth_client_secret,
    )
    async with AsyncApiClient(auth=auth) as client:
        first = await client.get("/v1/auth/me")
        assert first.status_code == 200
        token_after_first = auth._access_token
        second = await client.get("/v1/auth/me")
        assert second.status_code == 200
        assert auth._access_token == token_after_first  # reused

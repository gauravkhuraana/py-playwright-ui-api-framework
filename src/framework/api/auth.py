"""Authentication strategies matching the OpenAPI security schemes.

The Bill Payment API supports six schemes; we implement the four most useful
for automation: API key (header), Bearer JWT, Basic, and OAuth2
client_credentials with token caching.
"""

from __future__ import annotations

import base64
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


class AuthStrategy(ABC):
    """Strategy interface: mutates outgoing :class:`httpx.Request` headers."""

    @abstractmethod
    async def apply(self, request: httpx.Request, client: httpx.AsyncClient) -> None: ...


@dataclass
class ApiKeyAuth(AuthStrategy):
    api_key: str
    header_name: str = "X-API-Key"

    async def apply(self, request: httpx.Request, client: httpx.AsyncClient) -> None:
        request.headers[self.header_name] = self.api_key


@dataclass
class BearerAuth(AuthStrategy):
    token: str

    async def apply(self, request: httpx.Request, client: httpx.AsyncClient) -> None:
        request.headers["Authorization"] = f"Bearer {self.token}"


@dataclass
class BasicAuth(AuthStrategy):
    username: str
    password: str

    async def apply(self, request: httpx.Request, client: httpx.AsyncClient) -> None:
        token = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        request.headers["Authorization"] = f"Basic {token}"


@dataclass
class OAuth2ClientCredentialsAuth(AuthStrategy):
    """OAuth2 client_credentials with in-memory token caching.

    Refreshes 30 seconds before expiry to avoid edge-case races.
    """

    client_id: str
    client_secret: str
    token_url: str = "/oauth/token"
    scope: str | None = None
    _access_token: str | None = field(default=None, init=False, repr=False)
    _expires_at: float = field(default=0.0, init=False, repr=False)

    async def apply(self, request: httpx.Request, client: httpx.AsyncClient) -> None:
        if not self._access_token or time.time() >= self._expires_at - 30:
            await self._fetch_token(client)
        request.headers["Authorization"] = f"Bearer {self._access_token}"

    async def _fetch_token(self, client: httpx.AsyncClient) -> None:
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if self.scope:
            data["scope"] = self.scope
        # Use a bare request so the configured auth strategy is not re-applied.
        resp = await client.post(self.token_url, data=data, auth=None)
        resp.raise_for_status()
        payload = resp.json()
        self._access_token = payload["access_token"]
        self._expires_at = time.time() + float(payload.get("expires_in", 3600))

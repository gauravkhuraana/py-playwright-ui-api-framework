"""Authentication endpoints."""

from __future__ import annotations

from typing import Any

import httpx

from ..base_service import BaseService


class AuthService(BaseService):
    base_path = "/oauth/token"

    async def get_token(
        self,
        *,
        grant_type: str = "client_credentials",
        client_id: str | None = None,
        client_secret: str | None = None,
        username: str | None = None,
        password: str | None = None,
        refresh_token: str | None = None,
    ) -> httpx.Response:
        data: dict[str, Any] = {"grant_type": grant_type}
        for k, v in {
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
            "refresh_token": refresh_token,
        }.items():
            if v is not None:
                data[k] = v
        return await self._client.post(self.base_path, data=data)

    async def me(self) -> httpx.Response:
        return await self._client.get("/v1/auth/me")

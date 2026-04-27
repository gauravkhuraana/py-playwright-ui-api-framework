"""Health service (no auth required)."""

from __future__ import annotations

import httpx

from ..base_service import BaseService


class HealthService(BaseService):
    base_path = "/health"

    async def check(self) -> httpx.Response:
        return await self._client.get(self.base_path, expected_status=200)

    async def check_db(self) -> httpx.Response:
        return await self._client.get(f"{self.base_path}/db")

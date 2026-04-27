"""Bills service (``/v1/bills``)."""

from __future__ import annotations

from typing import Any

import httpx

from ..base_service import BaseService


class BillsService(BaseService):
    base_path = "/v1/bills"

    async def list(self, **filters: Any) -> httpx.Response:
        params = {k: v for k, v in filters.items() if v is not None}
        return await self._client.get(self.base_path, params=params)

    async def summary(self, *, user_id: str | None = None) -> httpx.Response:
        params = {"user_id": user_id} if user_id else None
        return await self._client.get(f"{self.base_path}/summary", params=params)

    async def overdue(
        self, *, page: int = 1, limit: int = 10, user_id: str | None = None
    ) -> httpx.Response:
        params: dict[str, Any] = {"page": page, "limit": limit}
        if user_id:
            params["user_id"] = user_id
        return await self._client.get(f"{self.base_path}/overdue", params=params)

    async def get(self, bill_id: str) -> httpx.Response:
        return await self._client.get(f"{self.base_path}/{bill_id}")

    async def create(self, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.post(self.base_path, json=payload)

    async def update(self, bill_id: str, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.put(f"{self.base_path}/{bill_id}", json=payload)

    async def patch(self, bill_id: str, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.patch(f"{self.base_path}/{bill_id}", json=payload)

    async def delete(self, bill_id: str) -> httpx.Response:
        return await self._client.delete(f"{self.base_path}/{bill_id}")

    async def fetch(self, bill_id: str) -> httpx.Response:
        return await self._client.post(f"{self.base_path}/{bill_id}/fetch")

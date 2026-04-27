"""Billers service (``/v1/billers``)."""

from __future__ import annotations

from typing import Any

import httpx

from ..base_service import BaseService


class BillersService(BaseService):
    base_path = "/v1/billers"

    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 10,
        category: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        fetch_bill_supported: bool | None = None,
    ) -> httpx.Response:
        params: dict[str, Any] = {"page": page, "limit": limit}
        if category is not None:
            params["category"] = category
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
        if search is not None:
            params["search"] = search
        if fetch_bill_supported is not None:
            params["fetch_bill_supported"] = str(fetch_bill_supported).lower()
        return await self._client.get(self.base_path, params=params)

    async def categories(self) -> httpx.Response:
        return await self._client.get(f"{self.base_path}/categories")

    async def get(self, biller_id: str) -> httpx.Response:
        return await self._client.get(f"{self.base_path}/{biller_id}")

    async def exists(self, biller_id: str) -> httpx.Response:
        return await self._client.head(f"{self.base_path}/{biller_id}")

    async def create(self, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.post(self.base_path, json=payload)

    async def update(self, biller_id: str, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.put(f"{self.base_path}/{biller_id}", json=payload)

    async def patch(self, biller_id: str, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.patch(f"{self.base_path}/{biller_id}", json=payload)

    async def delete(self, biller_id: str) -> httpx.Response:
        return await self._client.delete(f"{self.base_path}/{biller_id}")

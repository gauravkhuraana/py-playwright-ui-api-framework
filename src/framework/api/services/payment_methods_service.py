"""Payment Methods service (``/v1/payment-methods``)."""

from __future__ import annotations

from typing import Any

import httpx

from ..base_service import BaseService


class PaymentMethodsService(BaseService):
    base_path = "/v1/payment-methods"

    async def list(self, **filters: Any) -> httpx.Response:
        params = {k: v for k, v in filters.items() if v is not None}
        return await self._client.get(self.base_path, params=params)

    async def types(self) -> httpx.Response:
        return await self._client.get(f"{self.base_path}/types")

    async def get(self, method_id: str) -> httpx.Response:
        return await self._client.get(f"{self.base_path}/{method_id}")

    async def create(self, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.post(self.base_path, json=payload)

    async def update(self, method_id: str, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.put(f"{self.base_path}/{method_id}", json=payload)

    async def patch(self, method_id: str, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.patch(f"{self.base_path}/{method_id}", json=payload)

    async def delete(self, method_id: str) -> httpx.Response:
        return await self._client.delete(f"{self.base_path}/{method_id}")

    async def set_default(self, method_id: str) -> httpx.Response:
        return await self._client.post(f"{self.base_path}/{method_id}/set-default")

"""Payments service (``/v1/payments``)."""

from __future__ import annotations

from typing import Any

import httpx

from ..base_service import BaseService


class PaymentsService(BaseService):
    base_path = "/v1/payments"

    async def list(self, **filters: Any) -> httpx.Response:
        params = {k: v for k, v in filters.items() if v is not None}
        return await self._client.get(self.base_path, params=params)

    async def stats(self, *, user_id: str | None = None) -> httpx.Response:
        params = {"user_id": user_id} if user_id else None
        return await self._client.get(f"{self.base_path}/stats", params=params)

    async def get(self, payment_id: str) -> httpx.Response:
        return await self._client.get(f"{self.base_path}/{payment_id}")

    async def create(self, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.post(self.base_path, json=payload)

    async def delete(self, payment_id: str) -> httpx.Response:
        return await self._client.delete(f"{self.base_path}/{payment_id}")

    async def refund(
        self, payment_id: str, *, amount: float | None = None, reason: str | None = None
    ) -> httpx.Response:
        body: dict[str, Any] = {}
        if amount is not None:
            body["amount"] = amount
        if reason is not None:
            body["reason"] = reason
        return await self._client.post(f"{self.base_path}/{payment_id}/refund", json=body or None)

    async def cancel(self, payment_id: str) -> httpx.Response:
        return await self._client.post(f"{self.base_path}/{payment_id}/cancel")

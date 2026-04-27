"""Users service (``/v1/users``)."""

from __future__ import annotations

from typing import Any

import httpx

from ..base_service import BaseService


class UsersService(BaseService):
    base_path = "/v1/users"

    async def list(self, **filters: Any) -> httpx.Response:
        params = {k: v for k, v in filters.items() if v is not None}
        return await self._client.get(self.base_path, params=params)

    async def get(self, user_id: str) -> httpx.Response:
        return await self._client.get(f"{self.base_path}/{user_id}")

    async def create(self, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.post(self.base_path, json=payload)

    async def update(self, user_id: str, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.put(f"{self.base_path}/{user_id}", json=payload)

    async def patch(self, user_id: str, payload: dict[str, Any]) -> httpx.Response:
        return await self._client.patch(f"{self.base_path}/{user_id}", json=payload)

    async def delete(self, user_id: str) -> httpx.Response:
        return await self._client.delete(f"{self.base_path}/{user_id}")

    async def bills(self, user_id: str, *, page: int = 1, limit: int = 10) -> httpx.Response:
        return await self._client.get(
            f"{self.base_path}/{user_id}/bills", params={"page": page, "limit": limit}
        )

    async def payment_methods(self, user_id: str) -> httpx.Response:
        return await self._client.get(f"{self.base_path}/{user_id}/payment-methods")

    async def transactions(
        self, user_id: str, *, page: int = 1, limit: int = 10
    ) -> httpx.Response:
        return await self._client.get(
            f"{self.base_path}/{user_id}/transactions", params={"page": page, "limit": limit}
        )

    async def verify_kyc(self, user_id: str, status: str = "verified") -> httpx.Response:
        return await self._client.post(
            f"{self.base_path}/{user_id}/verify-kyc", json={"status": status}
        )

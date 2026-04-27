"""Files service (``/v1/files``) — multipart uploads."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import httpx

from ..base_service import BaseService


class FilesService(BaseService):
    base_path = "/v1/files"

    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 10,
        mime_type: str | None = None,
        user_id: str | None = None,
    ) -> httpx.Response:
        params: dict[str, Any] = {"page": page, "limit": limit}
        if mime_type:
            params["mime_type"] = mime_type
        if user_id:
            params["user_id"] = user_id
        return await self._client.get(self.base_path, params=params)

    async def upload(
        self,
        file_path: str | Path,
        *,
        description: str | None = None,
        category: str | None = None,
    ) -> httpx.Response:
        path = Path(file_path)
        files = {"file": (path.name, path.read_bytes())}
        data: dict[str, Any] = {}
        if description:
            data["description"] = description
        if category:
            data["category"] = category
        return await self._client.post(
            f"{self.base_path}/upload", files=files, data=data or None
        )

    async def upload_multiple(self, file_paths: Iterable[str | Path]) -> httpx.Response:
        files = []
        for fp in file_paths:
            p = Path(fp)
            files.append(("files", (p.name, p.read_bytes())))
        return await self._client.post(f"{self.base_path}/upload-multiple", files=files)

    async def get(self, file_id: str) -> httpx.Response:
        return await self._client.get(f"{self.base_path}/{file_id}")

    async def exists(self, file_id: str) -> httpx.Response:
        return await self._client.head(f"{self.base_path}/{file_id}")

    async def delete(self, file_id: str) -> httpx.Response:
        return await self._client.delete(f"{self.base_path}/{file_id}")

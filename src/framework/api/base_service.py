"""Base class for API service objects."""

from __future__ import annotations

from .client import AsyncApiClient


class BaseService:
    """Common functionality for all service objects."""

    base_path: str = ""

    def __init__(self, client: AsyncApiClient) -> None:
        self._client = client

    def _url(self, path: str = "") -> str:
        if not path:
            return self.base_path
        if path.startswith("/"):
            return path
        return f"{self.base_path.rstrip('/')}/{path.lstrip('/')}"

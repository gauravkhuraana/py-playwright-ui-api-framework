"""Async HTTP client wrapping :class:`httpx.AsyncClient`.

Adds:

* configurable :class:`AuthStrategy`
* automatic ``X-Request-Id`` correlation header
* :mod:`tenacity`-based retries on configured 5xx status codes and timeouts
* request/response Allure attachments (best-effort, no hard dependency)
* structured logging of every call
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Any, Self

import httpx
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

from ..config import Settings, get_settings
from ..logging import get_logger
from .auth import AuthStrategy

log = get_logger(__name__)


def _is_retryable(response: httpx.Response, retry_on: list[int]) -> bool:
    return response.status_code in retry_on


class AsyncApiClient:
    """High-level wrapper used by all service objects."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        auth: AuthStrategy | None = None,
        settings: Settings | None = None,
        timeout: float | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._auth = auth
        self._client = httpx.AsyncClient(
            base_url=base_url or str(self._settings.api_base_url),
            timeout=timeout or self._settings.api_timeout_s,
            http2=True,
            headers={"Accept": "application/json"},
        )

    # ----- lifecycle -------------------------------------------------------

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    @property
    def httpx_client(self) -> httpx.AsyncClient:
        """Expose the underlying client for niche cases (e.g. SSE, streaming)."""
        return self._client

    # ----- core request ----------------------------------------------------

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        headers: dict[str, str] | None = None,
        expected_status: int | tuple[int, ...] | None = None,
    ) -> httpx.Response:
        retry_cfg = self._settings.retry
        request_id = str(uuid.uuid4())
        merged_headers = {"X-Request-Id": request_id, **(headers or {})}

        async def _do_call() -> httpx.Response:
            req = self._client.build_request(
                method,
                url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=merged_headers,
            )
            if self._auth is not None:
                await self._auth.apply(req, self._client)
            log.info("api.request", method=method, url=url, request_id=request_id)
            resp = await self._client.send(req)
            log.info(
                "api.response",
                method=method,
                url=url,
                status=resp.status_code,
                request_id=request_id,
                elapsed_ms=int(resp.elapsed.total_seconds() * 1000),
            )
            self._attach_to_allure(req, resp)
            return resp

        try:
            retrying = AsyncRetrying(
                stop=stop_after_attempt(retry_cfg.max_attempts),
                wait=wait_exponential(multiplier=retry_cfg.backoff_factor, max=10),
                retry=(
                    retry_if_exception_type((httpx.TimeoutException, httpx.TransportError))
                    | retry_if_result(lambda r: _is_retryable(r, retry_cfg.retry_on_status))
                ),
                reraise=True,
            )
            response = await retrying(_do_call)
        except RetryError as exc:  # pragma: no cover - rare
            raise exc.last_attempt.exception() or exc from exc  # type: ignore[misc]

        if expected_status is not None:
            allowed = (
                (expected_status,) if isinstance(expected_status, int) else tuple(expected_status)
            )
            if response.status_code not in allowed:
                raise AssertionError(
                    f"Unexpected status {response.status_code} for {method} {url}: "
                    f"expected one of {allowed}. Body: {response.text[:500]}"
                )
        return response

    # ----- convenience verbs ----------------------------------------------

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("DELETE", url, **kwargs)

    async def head(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("HEAD", url, **kwargs)

    # ----- helpers --------------------------------------------------------

    @staticmethod
    def _attach_to_allure(req: httpx.Request, resp: httpx.Response) -> None:
        try:  # best-effort; never break tests if allure is not active
            import allure

            allure.attach(
                f"{req.method} {req.url}\n\n"
                f"Headers: {dict(req.headers)}\n\n"
                f"Body: {(req.content or b'').decode(errors='replace')[:4000]}",
                name="HTTP request",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                f"Status: {resp.status_code}\n\n"
                f"Headers: {dict(resp.headers)}\n\n"
                f"Body: {resp.text[:4000]}",
                name="HTTP response",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:  # pragma: no cover
            pass


@asynccontextmanager
async def api_client(
    *, auth: AuthStrategy | None = None, base_url: str | None = None
) -> AsyncIterator[AsyncApiClient]:
    """Async context manager helper for ad-hoc usage."""
    client = AsyncApiClient(auth=auth, base_url=base_url)
    try:
        yield client
    finally:
        await client.aclose()

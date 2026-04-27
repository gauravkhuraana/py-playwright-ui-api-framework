"""Smoke tests for the Health endpoints (no auth required)."""

from __future__ import annotations

import pytest

from src.framework.api.services import HealthService


@pytest.mark.smoke
@pytest.mark.api
async def test_health_endpoint_returns_200(health_service: HealthService) -> None:
    resp = await health_service.check()
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"


@pytest.mark.api
async def test_health_db_endpoint(health_service: HealthService) -> None:
    resp = await health_service.check_db()
    assert resp.status_code in (200, 503)
    assert "data" in resp.json()

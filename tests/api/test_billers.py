"""CRUD coverage for the Billers resource."""

from __future__ import annotations

import pytest

from src.framework.api.services import BillersService
from src.framework.data import BillerFactory


@pytest.mark.smoke
@pytest.mark.api
async def test_list_billers_paginated(billers_service: BillersService) -> None:
    resp = await billers_service.list(page=1, limit=5)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert body["meta"]["pagination"]["page"] == 1
    assert body["meta"]["pagination"]["limit"] == 5


@pytest.mark.api
async def test_filter_billers_by_category(billers_service: BillersService) -> None:
    resp = await billers_service.list(category="telecom", limit=20)
    assert resp.status_code == 200
    for biller in resp.json()["data"]:
        assert biller["category"] == "telecom"


@pytest.mark.api
async def test_list_biller_categories(billers_service: BillersService) -> None:
    resp = await billers_service.categories()
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.regression
@pytest.mark.api
async def test_create_and_delete_biller(billers_service: BillersService) -> None:
    payload = BillerFactory.build()
    create = await billers_service.create(payload)
    assert create.status_code in (201, 409), create.text
    if create.status_code == 409:
        pytest.skip("Biller already exists; skipping cleanup leg")
    biller_id = create.json()["data"]["id"]

    fetched = await billers_service.get(biller_id)
    assert fetched.status_code == 200
    assert fetched.json()["data"]["id"] == biller_id

    deleted = await billers_service.delete(biller_id)
    assert deleted.status_code == 200


@pytest.mark.api
async def test_create_biller_validation_error(billers_service: BillersService) -> None:
    resp = await billers_service.create({"name": "x"})  # missing required fields
    assert resp.status_code == 400
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"

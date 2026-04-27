"""API-layer fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from src.framework.api.services import BillersService, UsersService
from src.framework.data import BillerFactory, UserFactory


@pytest.fixture
async def created_user(users_service: UsersService) -> AsyncIterator[dict]:
    payload = UserFactory.build()
    resp = await users_service.create(payload)
    assert resp.status_code in (201, 409), resp.text
    user = resp.json()["data"] if resp.status_code == 201 else {"email": payload["email"]}
    yield user
    if "id" in user:
        await users_service.delete(user["id"])


@pytest.fixture
async def created_biller(billers_service: BillersService) -> AsyncIterator[dict]:
    payload = BillerFactory.build()
    resp = await billers_service.create(payload)
    assert resp.status_code in (201, 409), resp.text
    biller = resp.json()["data"] if resp.status_code == 201 else {"name": payload["name"]}
    yield biller
    if "id" in biller:
        await billers_service.delete(biller["id"])

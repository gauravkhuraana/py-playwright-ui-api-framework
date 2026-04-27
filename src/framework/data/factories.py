"""Faker-powered factories that build valid request payloads."""

from __future__ import annotations

import random
import string
from typing import Any

from faker import Faker

fake = Faker("en_IN")


def _slug(prefix: str, length: int = 6) -> str:
    return f"{prefix}-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class UserFactory:
    @staticmethod
    def build(**overrides: Any) -> dict[str, Any]:
        first = fake.first_name()
        last = fake.last_name()
        payload: dict[str, Any] = {
            "email": f"{first.lower()}.{last.lower()}.{_slug('u', 4)}@example.com",
            "phone": f"+91{fake.msisdn()[3:]}",
            "firstName": first,
            "lastName": last,
            "kycStatus": "pending",
            "address": {
                "line1": fake.street_address(),
                "city": fake.city(),
                "state": fake.state(),
                "postalCode": fake.postcode(),
                "country": "IN",
            },
        }
        payload.update(overrides)
        return payload


class BillerFactory:
    CATEGORIES = ("telecom", "electricity", "water", "gas", "broadband")

    @staticmethod
    def build(**overrides: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": _slug("biller"),
            "displayName": fake.company()[:90],
            "category": random.choice(BillerFactory.CATEGORIES),
            "description": fake.sentence(),
            "minAmount": 10,
            "maxAmount": 50_000,
            "fetchBillSupported": True,
            "partialPaymentAllowed": False,
            "supportedPaymentModes": ["upi", "credit_card", "debit_card"],
            "isActive": True,
        }
        payload.update(overrides)
        return payload


class BillFactory:
    @staticmethod
    def build(*, user_id: str, biller_id: str, **overrides: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "userId": user_id,
            "billerId": biller_id,
            "customerIdentifier": "".join(random.choices(string.digits, k=10)),
            "customerName": fake.name(),
            "nickname": fake.word().capitalize(),
            "amount": round(random.uniform(100, 5_000), 2),
            "currency": "INR",
            "dueDate": fake.future_date(end_date="+30d").isoformat(),
            "billPeriod": fake.month_name() + " " + str(fake.year()),
            "status": "pending",
        }
        payload.update(overrides)
        return payload


class PaymentMethodFactory:
    @staticmethod
    def build_upi(*, user_id: str, **overrides: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "userId": user_id,
            "type": "upi",
            "displayName": "UPI " + fake.first_name(),
            "upiId": f"{fake.user_name()}@okaxis",
            "isDefault": False,
        }
        payload.update(overrides)
        return payload

    @staticmethod
    def build_card(*, user_id: str, **overrides: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "userId": user_id,
            "type": "credit_card",
            "displayName": "HDFC Credit",
            "cardLastFour": "".join(random.choices(string.digits, k=4)),
            "cardNetwork": "visa",
            "cardExpiryMonth": random.randint(1, 12),
            "cardExpiryYear": 2028,
            "cardHolderName": fake.name().upper(),
            "isDefault": False,
        }
        payload.update(overrides)
        return payload

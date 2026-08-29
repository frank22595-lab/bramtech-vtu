"""
Mock provider for testing and demos.

Behaves like a real aggregator but returns predictable results
without hitting any external service. Use for:
  - Development before you have real Pairgate credentials
  - Automated tests
  - Manual sandbox demos to stakeholders

Behavior is controlled by the `mock_mode` config key:
  - "always_success": every call succeeds
  - "always_failed":  every call fails
  - "flaky":          alternates success/failure
"""
from __future__ import annotations

import itertools
import uuid
from decimal import Decimal
from typing import Any

from .base import BaseProvider, DeliveryResult, DeliveryStatus


class MockProvider(BaseProvider):
    code = "mock"
    display_name = "Mock Provider (test only)"

    _flaky_toggle = itertools.cycle([True, False])

    def _make_result(self, mode: str, amount: Decimal | None = None) -> DeliveryResult:
        provider_ref = f"MOCK-{uuid.uuid4().hex[:10].upper()}"
        if mode == "always_failed":
            return DeliveryResult(
                status=DeliveryStatus.FAILED,
                provider_reference=provider_ref,
                message="Mock failure",
                raw_response={"mock": True, "mode": mode},
            )
        if mode == "flaky":
            ok = next(self._flaky_toggle)
            if not ok:
                return DeliveryResult(
                    status=DeliveryStatus.FAILED,
                    provider_reference=provider_ref,
                    message="Flaky failure",
                    raw_response={"mock": True, "mode": mode},
                )
        # default: success
        return DeliveryResult(
            status=DeliveryStatus.SUCCESS,
            provider_reference=provider_ref,
            message="OK",
            raw_response={"mock": True, "mode": mode},
            actual_cost=amount,
        )

    def _mode(self) -> str:
        return self.config.get("mock_mode", "always_success")

    def buy_airtime(self, *, network, phone, amount, reference) -> DeliveryResult:
        return self._make_result(self._mode(), amount=amount)

    def buy_data(self, *, network, phone, sku_code, reference) -> DeliveryResult:
        return self._make_result(self._mode())

    def buy_cable(self, *, network, smartcard, sku_code, reference) -> DeliveryResult:
        return self._make_result(self._mode())

    def buy_electricity(self, *, disco, meter, amount, meter_type, reference) -> DeliveryResult:
        return self._make_result(self._mode(), amount=amount)

    def check_status(self, provider_reference: str) -> DeliveryResult:
        return DeliveryResult(
            status=DeliveryStatus.SUCCESS,
            provider_reference=provider_reference,
            message="Mock status check",
        )

    def get_balance(self) -> Decimal:
        return Decimal(self.config.get("mock_balance", "500000"))

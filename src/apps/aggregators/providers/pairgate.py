"""
Pairgate provider.

Real integration for https://pairgate.com API. Implementation follows the
common shape of Nigerian VTU aggregator APIs. When you get your actual
Pairgate credentials, verify the endpoint paths and payload shapes against
their current docs — this is a solid starting scaffold, but every aggregator
has small quirks.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

import httpx

from .base import (
    BaseProvider, DeliveryResult, DeliveryStatus,
    ProviderConfigurationError, ProviderError, ProviderTimeoutError,
)


class PairgateProvider(BaseProvider):
    code = "pairgate"
    display_name = "Pairgate"

    DEFAULT_TIMEOUT = 30.0  # seconds

    def _client(self) -> httpx.Client:
        api_key = self.config.get("api_key")
        base_url = self.aggregator.base_url or self.config.get("base_url")
        if not api_key or not base_url:
            raise ProviderConfigurationError(
                "Pairgate needs api_key and base_url in config"
            )
        return httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=self.DEFAULT_TIMEOUT,
        )

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            with self._client() as c:
                r = c.post(path, json=payload)
        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(str(e)) from e
        except httpx.HTTPError as e:
            raise ProviderError(f"HTTP error: {e}") from e

        try:
            data = r.json()
        except Exception:
            data = {"raw_body": r.text}

        return data

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            with self._client() as c:
                r = c.get(path, params=params)
        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(str(e)) from e
        except httpx.HTTPError as e:
            raise ProviderError(f"HTTP error: {e}") from e

        try:
            return r.json()
        except Exception:
            return {"raw_body": r.text}

    def _normalize(self, resp: dict[str, Any]) -> DeliveryResult:
        """
        Convert Pairgate's response into a normalized DeliveryResult.

        Adjust these key checks once you have real Pairgate response samples.
        Common patterns: {"status": "success", "reference": "...", "message": "..."}
        """
        status_raw = str(resp.get("status", "")).lower()
        reference = str(resp.get("reference") or resp.get("transaction_id") or "")
        message = str(resp.get("message") or resp.get("msg") or "")

        if status_raw in ("success", "successful", "delivered", "completed"):
            status = DeliveryStatus.SUCCESS
        elif status_raw in ("pending", "processing", "in_progress"):
            status = DeliveryStatus.PENDING
        elif status_raw in ("failed", "error", "declined"):
            status = DeliveryStatus.FAILED
        else:
            status = DeliveryStatus.UNKNOWN

        return DeliveryResult(
            status=status,
            provider_reference=reference,
            message=message,
            raw_response=resp,
        )

    # ---------------- Public methods ----------------

    def buy_airtime(self, *, network, phone, amount, reference) -> DeliveryResult:
        payload = {
            "network": network.lower(),
            "phone": phone,
            "amount": str(amount),
            "request_id": reference,
        }
        return self._normalize(self._post("/airtime", payload))

    def buy_data(self, *, network, phone, sku_code, reference) -> DeliveryResult:
        payload = {
            "network": network.lower(),
            "phone": phone,
            "plan": sku_code,
            "request_id": reference,
        }
        return self._normalize(self._post("/data", payload))

    def buy_cable(self, *, network, smartcard, sku_code, reference) -> DeliveryResult:
        payload = {
            "provider": network.lower(),
            "smartcard_number": smartcard,
            "plan": sku_code,
            "request_id": reference,
        }
        return self._normalize(self._post("/cable", payload))

    def buy_electricity(self, *, disco, meter, amount, meter_type, reference) -> DeliveryResult:
        payload = {
            "disco": disco.lower(),
            "meter_number": meter,
            "amount": str(amount),
            "meter_type": meter_type,  # "prepaid" or "postpaid"
            "request_id": reference,
        }
        return self._normalize(self._post("/electricity", payload))

    def check_status(self, provider_reference: str) -> DeliveryResult:
        return self._normalize(
            self._get("/status", params={"reference": provider_reference})
        )

    def get_balance(self) -> Decimal:
        resp = self._get("/balance")
        val = resp.get("balance") or resp.get("wallet_balance") or 0
        return Decimal(str(val))

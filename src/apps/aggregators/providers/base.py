"""
Abstract base class for aggregator providers.

Every real aggregator (Pairgate, VTU.ng, etc.) must subclass BaseProvider
and implement the four methods: buy_airtime, buy_data, buy_cable, buy_electricity.

Providers return a normalized DeliveryResult so the transaction pipeline
doesn't care which aggregator was used.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any


class DeliveryStatus(str, Enum):
    """Normalized status returned by any aggregator."""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"    # aggregator accepted but delivery not confirmed
    UNKNOWN = "unknown"    # network error, need to reconcile later


@dataclass
class DeliveryResult:
    """
    Normalized result from any aggregator.

    - status: normalized status
    - provider_reference: the aggregator's own transaction id (for reconciliation)
    - message: human-readable status message
    - raw_response: raw payload for logging/debug
    - actual_cost: what the aggregator actually charged us (may differ from quote)
    """
    status: DeliveryStatus
    provider_reference: str = ""
    message: str = ""
    raw_response: dict[str, Any] = field(default_factory=dict)
    actual_cost: Decimal | None = None

    @property
    def is_terminal(self) -> bool:
        """Terminal statuses can't change; the transaction is done."""
        return self.status in (DeliveryStatus.SUCCESS, DeliveryStatus.FAILED)


class ProviderError(Exception):
    """Raised by a provider when the request could not even be sent."""


class ProviderTimeoutError(ProviderError):
    """Request timed out — status is unknown; reconciliation needed."""


class ProviderConfigurationError(ProviderError):
    """Provider is misconfigured (missing credentials, bad URL)."""


class BaseProvider(ABC):
    """
    Abstract aggregator provider.

    Subclasses implement each service type. If a provider doesn't support
    a service, raise NotImplementedError and routing will skip it.
    """

    code: str = ""              # matches Aggregator.code
    display_name: str = ""

    def __init__(self, aggregator, config: dict[str, Any] | None = None):
        """
        Args:
            aggregator: the Aggregator model instance.
            config: credentials + settings (loaded from env by factory).
        """
        self.aggregator = aggregator
        self.config = config or {}

    # ---------------- Service methods ----------------

    @abstractmethod
    def buy_airtime(
        self, *, network: str, phone: str, amount: Decimal, reference: str,
    ) -> DeliveryResult:
        """Buy airtime for the given phone number."""
        ...

    @abstractmethod
    def buy_data(
        self, *, network: str, phone: str, sku_code: str, reference: str,
    ) -> DeliveryResult:
        """Buy a data bundle by SKU."""
        ...

    def buy_cable(
        self, *, network: str, smartcard: str, sku_code: str, reference: str,
    ) -> DeliveryResult:
        """Buy a cable TV subscription. Override if supported."""
        raise NotImplementedError(f"{self.code} does not support cable purchases")

    def buy_electricity(
        self, *, disco: str, meter: str, amount: Decimal, meter_type: str, reference: str,
    ) -> DeliveryResult:
        """Buy electricity units. Override if supported."""
        raise NotImplementedError(f"{self.code} does not support electricity purchases")

    def check_status(self, provider_reference: str) -> DeliveryResult:
        """
        Query the aggregator for the status of a previous transaction.
        Used by the reconciliation worker for PENDING/UNKNOWN transactions.
        Override in subclasses.
        """
        raise NotImplementedError(f"{self.code} does not support status checks")

    def get_balance(self) -> Decimal:
        """Return our current float balance with this aggregator."""
        raise NotImplementedError(f"{self.code} does not support balance queries")

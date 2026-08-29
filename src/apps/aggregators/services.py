"""
Provider factory + routing.

`get_provider(aggregator)` returns an instantiated BaseProvider subclass.

`select_route(variation)` returns the highest-priority healthy aggregator
for a variation, respecting circuit breaker state.

`record_success(aggregator)` and `record_failure(aggregator)` update the
health/circuit-breaker state after each dispatch.
"""
from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import (
    Aggregator, AggregatorHealth, AggregatorRoute, AggregatorSKU,
    AggregatorStatus, CircuitState,
)
from .providers.base import BaseProvider
from .providers.mock import MockProvider
from .providers.pairgate import PairgateProvider


class NoAvailableAggregatorError(Exception):
    """No aggregator is available for the requested variation."""


# Registry of built-in providers. Add more as we integrate them.
PROVIDER_REGISTRY: dict[str, type[BaseProvider]] = {
    "pairgate": PairgateProvider,
    "mock": MockProvider,
}


def _load_provider_config(aggregator: Aggregator) -> dict:
    """
    Load per-aggregator credentials from Django settings / env.
    Keeps secrets out of the DB.
    """
    if aggregator.code == "pairgate":
        return {
            "api_key": getattr(settings, "PAIRGATE_API_KEY", ""),
            "base_url": aggregator.base_url,
        }
    if aggregator.code == "mock":
        return {
            "mock_mode": getattr(settings, "MOCK_PROVIDER_MODE", "always_success"),
        }
    return {}


def get_provider(aggregator: Aggregator) -> BaseProvider:
    """Instantiate the correct provider class for this aggregator."""
    cls = PROVIDER_REGISTRY.get(aggregator.code)
    if cls is None:
        raise ValueError(f"Unknown provider code: {aggregator.code}")
    return cls(aggregator=aggregator, config=_load_provider_config(aggregator))


def select_route(variation) -> tuple[Aggregator, AggregatorSKU]:
    """
    Choose the best aggregator for a variation.

    Rules:
      - Aggregator must be ACTIVE
      - Its circuit must not be OPEN (or the cooldown must have expired)
      - Prefer lowest priority number (highest priority)
      - Must have an AggregatorSKU mapping for this variation

    Raises NoAvailableAggregatorError if nothing is available.
    """
    routes = (
        AggregatorRoute.objects
        .select_related("aggregator", "aggregator__health")
        .filter(variation=variation, is_active=True,
                aggregator__status=AggregatorStatus.ACTIVE)
        .order_by("priority")
    )

    for route in routes:
        agg = route.aggregator

        # Check health / circuit breaker
        health, _ = AggregatorHealth.objects.get_or_create(aggregator=agg)
        if not health.is_available:
            continue

        # Check SKU mapping exists
        try:
            sku = AggregatorSKU.objects.get(
                aggregator=agg, variation=variation, is_active=True,
            )
        except AggregatorSKU.DoesNotExist:
            continue

        return agg, sku

    raise NoAvailableAggregatorError(
        f"No available aggregator for variation {variation.pk}"
    )


# ---------------- Circuit breaker updates ----------------

FAILURE_THRESHOLD = 3            # trip circuit after this many consecutive failures
SUCCESS_THRESHOLD_HALF_OPEN = 1  # successes needed to close a half-open circuit
COOLDOWN_SECONDS = 300           # how long an open circuit stays open (5 min)


@transaction.atomic
def record_success(aggregator: Aggregator) -> None:
    """Called after a successful delivery — heals the circuit."""
    health, _ = AggregatorHealth.objects.select_for_update().get_or_create(aggregator=aggregator)
    health.consecutive_failures = 0
    health.consecutive_successes += 1
    health.last_success_at = timezone.now()

    if health.state == CircuitState.HALF_OPEN:
        if health.consecutive_successes >= SUCCESS_THRESHOLD_HALF_OPEN:
            health.state = CircuitState.CLOSED
            health.open_until = None
    elif health.state == CircuitState.OPEN:
        # Coming out of OPEN — go to half-open first
        health.state = CircuitState.HALF_OPEN

    health.save()


@transaction.atomic
def record_failure(aggregator: Aggregator) -> None:
    """Called after a failed delivery — may trip the circuit."""
    health, _ = AggregatorHealth.objects.select_for_update().get_or_create(aggregator=aggregator)
    health.consecutive_successes = 0
    health.consecutive_failures += 1
    health.last_failure_at = timezone.now()

    if health.consecutive_failures >= FAILURE_THRESHOLD:
        health.state = CircuitState.OPEN
        health.open_until = timezone.now() + timedelta(seconds=COOLDOWN_SECONDS)

    health.save()

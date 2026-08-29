"""Tests for aggregator routing, circuit breaker, and mock provider."""
from decimal import Decimal

import pytest

from apps.aggregators.models import (
    Aggregator, AggregatorHealth, AggregatorRoute, AggregatorSKU,
    AggregatorStatus, CircuitState,
)
from apps.aggregators.providers.base import DeliveryStatus
from apps.aggregators.providers.mock import MockProvider
from apps.aggregators.services import (
    FAILURE_THRESHOLD, NoAvailableAggregatorError,
    get_provider, record_failure, record_success, select_route,
)
from apps.services.models import (
    Network, Service, ServiceCategory, ServiceVariation, VariationType,
)


@pytest.fixture
def variation(db):
    svc = Service.objects.create(
        category=ServiceCategory.DATA, network=Network.MTN,
        name="MTN Data", slug="mtn-data",
    )
    return ServiceVariation.objects.create(
        service=svc, name="1GB", variation_type=VariationType.FIXED,
        variation_code="mtn_1gb", face_value=Decimal("500"),
    )


@pytest.fixture
def primary_agg(db):
    return Aggregator.objects.create(
        code="mock", name="Primary Mock", base_url="http://mock.local",
        status=AggregatorStatus.ACTIVE,
    )


@pytest.fixture
def secondary_agg(db):
    return Aggregator.objects.create(
        code="mock", name="Secondary Mock", base_url="http://mock2.local",
        status=AggregatorStatus.ACTIVE,
    )


@pytest.mark.django_db
class TestMockProvider:
    def test_always_success(self, primary_agg):
        p = MockProvider(aggregator=primary_agg, config={"mock_mode": "always_success"})
        r = p.buy_airtime(network="mtn", phone="08012345678", amount=Decimal("100"), reference="t1")
        assert r.status == DeliveryStatus.SUCCESS
        assert r.provider_reference.startswith("MOCK-")

    def test_always_failed(self, primary_agg):
        p = MockProvider(aggregator=primary_agg, config={"mock_mode": "always_failed"})
        r = p.buy_data(network="mtn", phone="08012345678", sku_code="mtn_1gb", reference="t2")
        assert r.status == DeliveryStatus.FAILED

    def test_get_balance(self, primary_agg):
        p = MockProvider(aggregator=primary_agg, config={"mock_balance": "123456"})
        assert p.get_balance() == Decimal("123456")


@pytest.mark.django_db
class TestRouteSelection:
    def _add_route(self, agg, variation, priority=100):
        AggregatorRoute.objects.create(
            aggregator=agg, variation=variation, priority=priority, is_active=True,
        )
        AggregatorSKU.objects.create(
            aggregator=agg, variation=variation,
            aggregator_sku_code=f"{agg.code}_sku", is_active=True,
        )

    def test_select_primary_when_healthy(self, variation, primary_agg, secondary_agg):
        self._add_route(primary_agg, variation, priority=1)
        self._add_route(secondary_agg, variation, priority=2)

        chosen, sku = select_route(variation)
        assert chosen.pk == primary_agg.pk

    def test_failover_to_secondary_when_primary_circuit_open(
        self, variation, primary_agg, secondary_agg,
    ):
        self._add_route(primary_agg, variation, priority=1)
        self._add_route(secondary_agg, variation, priority=2)

        # Trip primary's circuit
        for _ in range(FAILURE_THRESHOLD):
            record_failure(primary_agg)

        chosen, _ = select_route(variation)
        assert chosen.pk == secondary_agg.pk

    def test_no_available_aggregator_raises(self, variation, primary_agg):
        # Route exists but no SKU mapping
        AggregatorRoute.objects.create(
            aggregator=primary_agg, variation=variation, priority=1, is_active=True,
        )
        with pytest.raises(NoAvailableAggregatorError):
            select_route(variation)

    def test_skips_disabled_aggregator(self, variation, primary_agg, secondary_agg):
        self._add_route(primary_agg, variation, priority=1)
        self._add_route(secondary_agg, variation, priority=2)

        primary_agg.status = AggregatorStatus.DISABLED
        primary_agg.save()

        chosen, _ = select_route(variation)
        assert chosen.pk == secondary_agg.pk


@pytest.mark.django_db
class TestCircuitBreaker:
    def test_starts_closed(self, primary_agg):
        h, _ = AggregatorHealth.objects.get_or_create(aggregator=primary_agg)
        assert h.state == CircuitState.CLOSED
        assert h.is_available

    def test_trips_open_after_threshold_failures(self, primary_agg):
        for _ in range(FAILURE_THRESHOLD):
            record_failure(primary_agg)

        h = AggregatorHealth.objects.get(aggregator=primary_agg)
        assert h.state == CircuitState.OPEN
        assert not h.is_available

    def test_success_resets_failure_counter(self, primary_agg):
        record_failure(primary_agg)
        record_failure(primary_agg)
        record_success(primary_agg)

        h = AggregatorHealth.objects.get(aggregator=primary_agg)
        assert h.consecutive_failures == 0
        assert h.state == CircuitState.CLOSED

    def test_success_after_open_transitions_to_half_open_then_closed(self, primary_agg):
        # Trip open
        for _ in range(FAILURE_THRESHOLD):
            record_failure(primary_agg)
        h = AggregatorHealth.objects.get(aggregator=primary_agg)
        assert h.state == CircuitState.OPEN

        # First success -> half_open
        record_success(primary_agg)
        h.refresh_from_db()
        assert h.state == CircuitState.HALF_OPEN

        # Another success -> closed
        record_success(primary_agg)
        h.refresh_from_db()
        assert h.state == CircuitState.CLOSED

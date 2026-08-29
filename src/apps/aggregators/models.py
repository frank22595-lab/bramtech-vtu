"""
Aggregator models.

- Aggregator: a registered upstream VTU provider (Pairgate, VTU.ng, etc.)
- AggregatorSKU: maps our ServiceVariation to the aggregator's own SKU code
- AggregatorRoute: which aggregators can handle a variation, in priority order
- AggregatorHealth: real-time circuit-breaker state per aggregator
"""
from __future__ import annotations

import uuid

from django.db import models
from django.utils import timezone


class AggregatorStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused (temporary)"
    DISABLED = "disabled", "Disabled"


class Aggregator(models.Model):
    """
    A registered upstream VTU provider.

    Credentials are stored encrypted (via env vars, not this table).
    This table holds routing/metadata only.
    """
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.SlugField(max_length=50, unique=True, db_index=True,
                            help_text="Machine identifier, e.g. 'pairgate', 'vtung'")
    name = models.CharField(max_length=100, help_text="Human name, e.g. 'Pairgate'")
    base_url = models.URLField()
    status = models.CharField(
        max_length=20,
        choices=AggregatorStatus.choices,
        default=AggregatorStatus.ACTIVE,
        db_index=True,
    )

    # Link to ledger account holding our float with this aggregator
    ledger_account_code = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. 'aggregator_float:pairgate' — must exist in ledger",
    )

    # Notification thresholds
    low_balance_alert_naira = models.DecimalField(
        max_digits=12, decimal_places=2, default=10000,
        help_text="Alert when our float drops below this",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "aggregators_aggregator"

    def __str__(self) -> str:
        return self.name


class AggregatorSKU(models.Model):
    """
    Maps our internal ServiceVariation to the SKU code an aggregator uses.

    Example: our variation "mtn_1gb_sme_7d" might map to Pairgate's "mtn-sme1"
    and VTU.ng's "MTN_1GB_7D".
    """
    aggregator = models.ForeignKey(
        Aggregator, on_delete=models.CASCADE, related_name="skus",
    )
    variation = models.ForeignKey(
        "services.ServiceVariation",
        on_delete=models.CASCADE,
        related_name="aggregator_skus",
    )
    aggregator_sku_code = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "aggregators_sku"
        unique_together = ("aggregator", "variation")
        indexes = [
            models.Index(fields=["aggregator", "variation", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.aggregator.code}:{self.aggregator_sku_code}"


class AggregatorRoute(models.Model):
    """
    Which aggregators serve which service variation, and in what order.

    Lower priority = tried first. Multiple routes per variation enable failover.
    """
    variation = models.ForeignKey(
        "services.ServiceVariation",
        on_delete=models.CASCADE,
        related_name="routes",
    )
    aggregator = models.ForeignKey(
        Aggregator, on_delete=models.CASCADE, related_name="routes",
    )
    priority = models.IntegerField(default=100, help_text="Lower = tried first")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "aggregators_route"
        unique_together = ("variation", "aggregator")
        ordering = ["priority"]
        indexes = [
            models.Index(fields=["variation", "priority", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.variation.name} -> {self.aggregator.code} (p={self.priority})"


class CircuitState(models.TextChoices):
    CLOSED = "closed", "Closed (healthy)"
    OPEN = "open", "Open (failing — traffic diverted)"
    HALF_OPEN = "half_open", "Half-open (probing recovery)"


class AggregatorHealth(models.Model):
    """
    Circuit-breaker state for an aggregator.

    Updated by the transaction pipeline and the health monitor task:
      - After N consecutive failures, state = OPEN (skip this aggregator)
      - After cooldown, state = HALF_OPEN (send one probe)
      - On probe success, state = CLOSED again
    """
    aggregator = models.OneToOneField(
        Aggregator, on_delete=models.CASCADE, related_name="health",
    )
    state = models.CharField(
        max_length=20,
        choices=CircuitState.choices,
        default=CircuitState.CLOSED,
        db_index=True,
    )
    consecutive_failures = models.IntegerField(default=0)
    consecutive_successes = models.IntegerField(default=0)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    open_until = models.DateTimeField(null=True, blank=True,
                                       help_text="When circuit auto-transitions to half-open")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "aggregators_health"

    def __str__(self) -> str:
        return f"{self.aggregator.code}: {self.state}"

    @property
    def is_available(self) -> bool:
        """Can this aggregator receive traffic right now?"""
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.HALF_OPEN:
            return True
        # OPEN — check if cooldown has expired
        if self.open_until and timezone.now() >= self.open_until:
            return True  # ready for a half-open probe
        return False

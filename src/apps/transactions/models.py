"""
Transaction model — the user-facing record of every purchase.

Lifecycle (state machine):

  PENDING     -> money not yet debited from wallet
  PROCESSING  -> money debited, dispatched to aggregator, awaiting result
  SUCCESS     -> aggregator confirmed delivery
  FAILED      -> aggregator failed AND wallet was refunded
  REFUNDED    -> like SUCCESS but manually reversed later

Rules enforced by TransactionService:
  - Never mutate a terminal transaction (SUCCESS/FAILED/REFUNDED)
  - Every state change is timestamped
  - PROCESSING transactions have exactly one associated debit journal
  - FAILED transactions have both a debit journal AND a reversing refund journal
"""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class TransactionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class TransactionType(models.TextChoices):
    AIRTIME = "airtime", "Airtime"
    DATA = "data", "Data"
    CABLE_TV = "cable_tv", "Cable TV"
    ELECTRICITY = "electricity", "Electricity"
    EDUCATION = "education", "Education Pin"
    BETTING = "betting", "Betting"
    OTHER = "other", "Other"


class Transaction(models.Model):
    """
    User-facing purchase record.

    Immutable in spirit — status is mutated only through TransactionService.
    """
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    # Nice human ref shown to users (e.g. "BRT-000012345")
    reference = models.CharField(max_length=100, unique=True, db_index=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    transaction_type = models.CharField(
        max_length=20, choices=TransactionType.choices, db_index=True,
    )
    variation = models.ForeignKey(
        "services.ServiceVariation",
        on_delete=models.PROTECT,
        related_name="transactions",
    )

    # The delivery target (phone / meter / smartcard / betting username)
    recipient = models.CharField(max_length=100, help_text="Phone / meter / smartcard / etc.")
    recipient_meta = models.JSONField(default=dict, blank=True,
                                       help_text="Any extra fields (meter_type, customer_name)")

    # Money
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                  help_text="Face value the user 'bought'")
    sale_price = models.DecimalField(max_digits=12, decimal_places=2,
                                      help_text="What we charged the user")
    cost_price = models.DecimalField(max_digits=12, decimal_places=2,
                                      help_text="What we paid the aggregator")
    margin = models.DecimalField(max_digits=12, decimal_places=2,
                                  help_text="sale_price - cost_price")

    # Idempotency key (client-supplied, e.g. from mobile app UUID)
    idempotency_key = models.CharField(max_length=100, db_index=True)

    # Aggregator routing
    aggregator = models.ForeignKey(
        "aggregators.Aggregator",
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    aggregator_reference = models.CharField(max_length=100, blank=True, db_index=True)
    aggregator_response = models.JSONField(default=dict, blank=True)

    # Status tracking
    status = models.CharField(
        max_length=20, choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING, db_index=True,
    )
    status_message = models.CharField(max_length=500, blank=True)

    # Journal links
    debit_journal = models.ForeignKey(
        "ledger.Journal", null=True, blank=True,
        on_delete=models.PROTECT, related_name="+",
    )
    refund_journal = models.ForeignKey(
        "ledger.Journal", null=True, blank=True,
        on_delete=models.PROTECT, related_name="+",
    )

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    processing_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Retry tracking (for reconciliation worker)
    delivery_attempts = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "transactions_transaction"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["transaction_type", "-created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "idempotency_key"],
                name="tx_user_idempotency_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.reference} [{self.status}]"

    @property
    def is_terminal(self) -> bool:
        return self.status in (
            TransactionStatus.SUCCESS,
            TransactionStatus.FAILED,
            TransactionStatus.REFUNDED,
        )

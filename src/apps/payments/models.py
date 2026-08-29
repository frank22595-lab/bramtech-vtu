"""
Payments models.

- VirtualAccount: Monnify-issued dedicated bank account per user
- FundingEvent: every incoming payment (bank transfer via Monnify, card, etc.)
- WebhookInbox: raw log of every inbound webhook for idempotency + audit
"""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class PaymentProvider(models.TextChoices):
    MONNIFY = "monnify", "Monnify"
    PAYSTACK = "paystack", "Paystack"
    FLUTTERWAVE = "flutterwave", "Flutterwave"


class VirtualAccount(models.Model):
    """Dedicated virtual account provisioned for a user by Monnify."""
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="virtual_accounts",
    )
    provider = models.CharField(
        max_length=20, choices=PaymentProvider.choices,
        default=PaymentProvider.MONNIFY,
    )
    account_number = models.CharField(max_length=20, unique=True, db_index=True)
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=200)
    provider_reference = models.CharField(max_length=100, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "payments_virtual_account"

    def __str__(self) -> str:
        return f"{self.account_number} - {self.bank_name}"


class FundingStatus(models.TextChoices):
    RECEIVED = "received", "Received"
    APPLIED = "applied", "Applied to wallet"
    FAILED = "failed", "Failed"
    REVERSED = "reversed", "Reversed"


class FundingEvent(models.Model):
    """
    Records every incoming payment. One row per Monnify transaction reference.

    Once APPLIED, the ledger has been credited and the wallet balance reflects it.
    Reprocessing the same provider_reference is prevented by unique_together.
    """
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="funding_events",
    )
    provider = models.CharField(max_length=20, choices=PaymentProvider.choices)
    provider_reference = models.CharField(max_length=100, db_index=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=20, choices=FundingStatus.choices,
        default=FundingStatus.RECEIVED, db_index=True,
    )
    ledger_journal = models.ForeignKey(
        "ledger.Journal", null=True, blank=True,
        on_delete=models.PROTECT, related_name="+",
    )

    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payments_funding_event"
        unique_together = ("provider", "provider_reference")
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.provider_reference} ({self.status})"


class WebhookInbox(models.Model):
    """
    Immutable log of every inbound webhook.
    Uses (provider, event_id) for idempotency — a repeated event is ignored.
    """
    provider = models.CharField(max_length=20, choices=PaymentProvider.choices)
    event_id = models.CharField(max_length=200, db_index=True)
    signature_verified = models.BooleanField(default=False)
    payload = models.JSONField()
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True)
    received_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "payments_webhook_inbox"
        unique_together = ("provider", "event_id")
        indexes = [
            models.Index(fields=["provider", "-received_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.event_id}"

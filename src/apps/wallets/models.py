"""
Wallet model.

A Wallet is a thin, user-facing object that owns a ledger Account.
The actual money math lives entirely in the ledger — the wallet just
provides a friendly API surface and holds user-specific rules
(daily limits, status flags, etc.).
"""
from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class WalletStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    FROZEN = "frozen", "Frozen"          # Temporarily blocked (fraud review)
    SUSPENDED = "suspended", "Suspended"  # Permanently disabled


class Wallet(models.Model):
    """
    User wallet — owns exactly one ledger Account of type USER_WALLET.

    All debits and credits go through WalletService, which posts to the
    linked ledger account via LedgerService.

    Balance is NEVER stored here — always computed from the ledger.
    """

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="wallet",
    )
    account = models.OneToOneField(
        "ledger.Account",
        on_delete=models.PROTECT,
        related_name="wallet",
    )

    status = models.CharField(
        max_length=20,
        choices=WalletStatus.choices,
        default=WalletStatus.ACTIVE,
        db_index=True,
    )

    # For audit + fraud analysis
    frozen_reason = models.TextField(blank=True)
    frozen_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wallets_wallet"
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Wallet({self.user.phone_number})"

    @property
    def balance(self) -> Decimal:
        """Current wallet balance, computed from the ledger."""
        return self.account.balance()

    @property
    def is_transactable(self) -> bool:
        return self.status == WalletStatus.ACTIVE

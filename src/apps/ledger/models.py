"""
Ledger models — the immutable double-entry accounting core.

Design principles:
1. Every naira has a source and destination account (double-entry).
2. Ledger entries are append-only — NEVER updated, NEVER deleted.
3. For any journal, SUM(entries.amount) MUST equal 0 (enforced by DB trigger).
4. Account balance = SUM(entries.amount) — never stored, always computed.
5. Corrections are made by posting reversing journals, not modifying entries.

This design mirrors how banks and Stripe do their books. It's the only
architecture that survives audits, disputes, and edge cases.
"""
from __future__ import annotations

import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class AccountType(models.TextChoices):
    """
    Account types define the semantics of what each account holds.

    - USER_WALLET: end-user's spendable balance
    - PLATFORM_REVENUE: our earned margin (income account)
    - AGGREGATOR_FLOAT: our balance sitting with Pairgate/VTU.ng (asset account)
    - REFUND_POOL: reserved for pending refunds (liability)
    - PROMOTIONAL_CREDIT: cashback/bonus given to users (expense)
    - RESELLER_COMMISSION_PAYABLE: owed to resellers (liability)
    - PENDING_SETTLEMENT: money in from Monnify not yet reconciled (liability)
    - PLATFORM_EXPENSE: fees paid out (Monnify charges etc.) (expense)
    - SUSPENSE: catch-all for unidentified transactions pending review
    """
    USER_WALLET = "user_wallet", "User Wallet"
    PLATFORM_REVENUE = "platform_revenue", "Platform Revenue"
    AGGREGATOR_FLOAT = "aggregator_float", "Aggregator Float"
    REFUND_POOL = "refund_pool", "Refund Pool"
    PROMOTIONAL_CREDIT = "promotional_credit", "Promotional Credit"
    RESELLER_COMMISSION_PAYABLE = "reseller_commission_payable", "Reseller Commission Payable"
    PENDING_SETTLEMENT = "pending_settlement", "Pending Settlement"
    PLATFORM_EXPENSE = "platform_expense", "Platform Expense"
    SUSPENSE = "suspense", "Suspense"


class JournalType(models.TextChoices):
    """
    Journal types classify why an entry was posted.
    Purely descriptive — the LedgerService enforces which types can do what.
    """
    FUNDING = "funding", "Wallet Funding"
    PURCHASE = "purchase", "Service Purchase"
    REFUND = "refund", "Refund"
    COMMISSION = "commission", "Reseller Commission"
    REVERSAL = "reversal", "Manual Reversal"
    ADJUSTMENT = "adjustment", "Manual Adjustment"
    PAYOUT = "payout", "Commission Payout"
    FEE = "fee", "Platform Fee"


class Account(models.Model):
    """
    A ledger account — a bucket that holds money (real or virtual).

    Each user's wallet gets one USER_WALLET account.
    Each aggregator gets one AGGREGATOR_FLOAT account.
    The business has one PLATFORM_REVENUE, one PLATFORM_EXPENSE, etc.

    We NEVER store a `balance` column here — balance is always derived
    from ledger_entries. Storing it invites drift and race conditions.
    """
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    account_type = models.CharField(
        max_length=40,
        choices=AccountType.choices,
        db_index=True,
    )
    # Human-readable code, unique across accounts of the same type
    # e.g. "user_wallet:00123", "aggregator_float:pairgate", "platform_revenue:main"
    code = models.CharField(max_length=100, unique=True, db_index=True)

    # Optional link to the user this account belongs to
    # (only set for USER_WALLET accounts)
    owner = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="ledger_accounts",
    )

    # Currency (we only do NGN for now but plan ahead)
    currency = models.CharField(max_length=3, default="NGN")

    # Description for humans
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "ledger_account"
        indexes = [
            models.Index(fields=["account_type", "is_active"]),
            models.Index(fields=["owner"]),
        ]

    def __str__(self) -> str:
        return f"[{self.account_type}] {self.code}"

    def balance(self) -> Decimal:
        """
        Compute current balance from ledger entries.
        This is the ONLY correct way to know a balance.
        """
        result = self.entries.aggregate(total=models.Sum("amount"))
        return result["total"] or Decimal("0")


class Journal(models.Model):
    """
    A journal groups related ledger entries that must be posted atomically.

    Every business event (a purchase, a refund, a funding) creates ONE journal
    with multiple ledger entries whose amounts sum to zero.

    Once posted, a journal is immutable. Corrections happen via new REVERSAL
    journals that mirror the original entries.
    """
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    journal_type = models.CharField(
        max_length=20,
        choices=JournalType.choices,
        db_index=True,
    )
    # External reference — order ID, transaction ID, webhook event ID, etc.
    reference = models.CharField(max_length=100, db_index=True)

    # Human description
    description = models.TextField(blank=True)

    # Idempotency: same (journal_type, reference) can only exist once.
    # Prevents accidental double-posting on retries.
    class Meta:
        db_table = "ledger_journal"
        unique_together = ("journal_type", "reference")
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    # If this journal reverses another, link to it (audit trail)
    reverses = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reversed_by",
    )

    def __str__(self) -> str:
        return f"{self.journal_type}:{self.reference}"

    def is_balanced(self) -> bool:
        """
        Verify entries sum to zero. Should ALWAYS be True — enforced by
        LedgerService and DB trigger. This is a diagnostic method.
        """
        total = self.entries.aggregate(total=models.Sum("amount"))["total"] or Decimal("0")
        return total == Decimal("0")


class LedgerEntry(models.Model):
    """
    A single debit or credit posting against an account.

    IMMUTABLE. No updates. No deletes. Only inserts.

    - Positive amount = credit (money INTO the account)
    - Negative amount = debit (money OUT of the account)

    The sum of all entries in a journal MUST equal zero (double-entry).
    The DB enforces this via a trigger — do not rely on application code alone.
    """
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    journal = models.ForeignKey(
        Journal,
        on_delete=models.PROTECT,
        related_name="entries",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="entries",
    )

    # Signed amount: positive = credit, negative = debit
    # Using 18 digits total, 2 decimal places -> max ₦9,999,999,999,999,999.99
    # That's ~10 quadrillion NGN. Plenty.
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )

    currency = models.CharField(max_length=3, default="NGN")

    # Human-readable narration
    description = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "ledger_entry"
        indexes = [
            models.Index(fields=["account", "-created_at"]),
            models.Index(fields=["journal"]),
        ]
        # Ensure no zero-amount entries pollute the ledger
        constraints = [
            models.CheckConstraint(
                check=~models.Q(amount=0),
                name="ledger_entry_amount_nonzero",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.account.code} {self.amount:+}"

    def save(self, *args, **kwargs) -> None:
        # Enforce immutability at the model layer as well as the DB
        if self.pk is not None:
            raise ValueError(
                "LedgerEntry is immutable. "
                "Create a reversing journal instead of updating."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        raise ValueError(
            "LedgerEntry cannot be deleted. "
            "Create a reversing journal instead."
        )

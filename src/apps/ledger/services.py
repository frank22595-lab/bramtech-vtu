"""
LedgerService — the single entrypoint for posting to the ledger.

NEVER create LedgerEntry objects directly outside this service.
Always go through post_journal() which enforces:
  - Journal balance = 0 (double-entry rule)
  - Atomic all-or-nothing insertion
  - Idempotency via (journal_type, reference)
  - Currency consistency across entries in a journal
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from django.db import IntegrityError, transaction

from .models import Account, Journal, JournalType, LedgerEntry


class LedgerError(Exception):
    """Base class for ledger errors."""


class UnbalancedJournalError(LedgerError):
    """Raised when the entries in a journal do not sum to zero."""


class DuplicateJournalError(LedgerError):
    """Raised when a journal with the same (type, reference) already exists."""


class MixedCurrencyError(LedgerError):
    """Raised when entries in a single journal use different currencies."""


@dataclass(frozen=True)
class EntrySpec:
    """
    A single line to post in a journal.

    amount is signed: positive = credit into account, negative = debit out.
    """
    account: Account
    amount: Decimal
    description: str = ""

    def __post_init__(self) -> None:
        # Coerce to Decimal for safety
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        if self.amount == 0:
            raise ValueError("Entry amount must not be zero")


class LedgerService:
    """
    The ONLY sanctioned way to write to the ledger.
    """

    @staticmethod
    @transaction.atomic
    def post_journal(
        *,
        journal_type: JournalType | str,
        reference: str,
        entries: Iterable[EntrySpec],
        description: str = "",
        reverses: Journal | None = None,
    ) -> Journal:
        """
        Post a balanced journal with its entries. Atomic.

        Args:
            journal_type: One of JournalType.
            reference: External identifier (transaction id, webhook event id).
                       Must be unique per journal_type (idempotency guard).
            entries: Iterable of EntrySpec. Must sum to zero.
            description: Optional human description.
            reverses: If this journal reverses another, pass the original.

        Returns:
            The saved Journal instance (with entries attached).

        Raises:
            UnbalancedJournalError: entries don't sum to zero.
            DuplicateJournalError: (journal_type, reference) already exists.
            MixedCurrencyError: entries use different currencies.
        """
        entries = list(entries)
        if len(entries) < 2:
            raise UnbalancedJournalError(
                f"A journal needs at least 2 entries; got {len(entries)}"
            )

        # Enforce single currency per journal
        currencies = {e.account.currency for e in entries}
        if len(currencies) > 1:
            raise MixedCurrencyError(
                f"All entries in a journal must share a currency; got {currencies}"
            )
        currency = currencies.pop()

        # Enforce balance rule
        total = sum((e.amount for e in entries), start=Decimal("0"))
        if total != Decimal("0"):
            raise UnbalancedJournalError(
                f"Entries must sum to 0; got {total} for reference={reference}"
            )

        # Create the journal (unique_together enforces idempotency)
        try:
            journal = Journal.objects.create(
                journal_type=journal_type,
                reference=reference,
                description=description,
                reverses=reverses,
            )
        except IntegrityError as e:
            raise DuplicateJournalError(
                f"Journal already exists for {journal_type}:{reference}"
            ) from e

        # Bulk-create the entries in one query
        LedgerEntry.objects.bulk_create([
            LedgerEntry(
                journal=journal,
                account=spec.account,
                amount=spec.amount,
                currency=currency,
                description=spec.description or description,
            )
            for spec in entries
        ])

        return journal

    @staticmethod
    @transaction.atomic
    def reverse_journal(
        original: Journal,
        *,
        reference: str,
        description: str = "",
    ) -> Journal:
        """
        Post a reversing journal that mirrors the original's entries.

        Every entry in the original gets a matching entry with negated amount.
        Original journal remains intact; the two together sum to zero.

        Args:
            original: The journal being reversed.
            reference: Unique reference for the reversal journal.
            description: Optional description of why the reversal happened.
        """
        entries = [
            EntrySpec(
                account=entry.account,
                amount=-entry.amount,
                description=f"Reversal of {entry.description}" if entry.description else "",
            )
            for entry in original.entries.all()
        ]

        return LedgerService.post_journal(
            journal_type=JournalType.REVERSAL,
            reference=reference,
            entries=entries,
            description=description or f"Reversal of {original.reference}",
            reverses=original,
        )

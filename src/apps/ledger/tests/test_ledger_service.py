"""
Tests for LedgerService.

These tests are the safety net for the entire financial system.
If any of them fail, DO NOT ship. Something is wrong at the core.
"""
from decimal import Decimal

import pytest

from apps.ledger.models import Account, AccountType, Journal, JournalType, LedgerEntry
from apps.ledger.services import (
    DuplicateJournalError,
    EntrySpec,
    LedgerService,
    UnbalancedJournalError,
)


@pytest.fixture
def wallet_account(db):
    return Account.objects.create(
        account_type=AccountType.USER_WALLET,
        code="user_wallet:test1",
        name="Test user wallet",
    )


@pytest.fixture
def revenue_account(db):
    return Account.objects.create(
        account_type=AccountType.PLATFORM_REVENUE,
        code="platform_revenue:main",
        name="Platform revenue",
    )


@pytest.fixture
def aggregator_account(db):
    return Account.objects.create(
        account_type=AccountType.AGGREGATOR_FLOAT,
        code="aggregator_float:pairgate",
        name="Pairgate float",
    )


@pytest.mark.django_db
class TestPostJournalBasics:
    def test_simple_balanced_journal_succeeds(self, wallet_account, aggregator_account, revenue_account):
        journal = LedgerService.post_journal(
            journal_type=JournalType.PURCHASE,
            reference="tx-001",
            entries=[
                EntrySpec(wallet_account, Decimal("-300")),          # user pays ₦300
                EntrySpec(aggregator_account, Decimal("285")),       # aggregator gets ₦285
                EntrySpec(revenue_account, Decimal("15")),           # we keep ₦15
            ],
        )
        assert journal.pk is not None
        assert journal.entries.count() == 3
        assert journal.is_balanced()

    def test_unbalanced_journal_rejected(self, wallet_account, aggregator_account):
        with pytest.raises(UnbalancedJournalError):
            LedgerService.post_journal(
                journal_type=JournalType.PURCHASE,
                reference="tx-002",
                entries=[
                    EntrySpec(wallet_account, Decimal("-300")),
                    EntrySpec(aggregator_account, Decimal("200")),  # doesn't balance!
                ],
            )
        # No journal or entries should have been created
        assert Journal.objects.filter(reference="tx-002").count() == 0
        assert LedgerEntry.objects.count() == 0

    def test_single_entry_journal_rejected(self, wallet_account):
        with pytest.raises(UnbalancedJournalError):
            LedgerService.post_journal(
                journal_type=JournalType.PURCHASE,
                reference="tx-003",
                entries=[EntrySpec(wallet_account, Decimal("100"))],
            )

    def test_zero_amount_entry_rejected(self, wallet_account, revenue_account):
        # This should fail at EntrySpec construction
        with pytest.raises(ValueError):
            EntrySpec(wallet_account, Decimal("0"))


@pytest.mark.django_db
class TestIdempotency:
    def test_duplicate_reference_rejected(self, wallet_account, aggregator_account, revenue_account):
        LedgerService.post_journal(
            journal_type=JournalType.PURCHASE,
            reference="tx-100",
            entries=[
                EntrySpec(wallet_account, Decimal("-100")),
                EntrySpec(aggregator_account, Decimal("95")),
                EntrySpec(revenue_account, Decimal("5")),
            ],
        )

        with pytest.raises(DuplicateJournalError):
            LedgerService.post_journal(
                journal_type=JournalType.PURCHASE,
                reference="tx-100",  # same reference
                entries=[
                    EntrySpec(wallet_account, Decimal("-100")),
                    EntrySpec(aggregator_account, Decimal("95")),
                    EntrySpec(revenue_account, Decimal("5")),
                ],
            )

        # Only one journal should exist
        assert Journal.objects.filter(reference="tx-100").count() == 1

    def test_same_reference_different_type_allowed(self, wallet_account, revenue_account):
        # Same reference is fine if journal type differs
        LedgerService.post_journal(
            journal_type=JournalType.PURCHASE,
            reference="X-1",
            entries=[
                EntrySpec(wallet_account, Decimal("-100")),
                EntrySpec(revenue_account, Decimal("100")),
            ],
        )
        LedgerService.post_journal(
            journal_type=JournalType.REFUND,
            reference="X-1",
            entries=[
                EntrySpec(wallet_account, Decimal("100")),
                EntrySpec(revenue_account, Decimal("-100")),
            ],
        )
        assert Journal.objects.filter(reference="X-1").count() == 2


@pytest.mark.django_db
class TestBalanceComputation:
    def test_balance_reflects_entries(self, wallet_account, aggregator_account, revenue_account):
        # Start at 0
        assert wallet_account.balance() == Decimal("0")

        # Fund the wallet with ₦1,000
        LedgerService.post_journal(
            journal_type=JournalType.FUNDING,
            reference="fund-1",
            entries=[
                EntrySpec(wallet_account, Decimal("1000")),
                EntrySpec(aggregator_account, Decimal("-1000")),  # temporarily using aggregator as source
            ],
        )
        assert wallet_account.balance() == Decimal("1000")

        # Buy a ₦300 service (₦15 profit)
        LedgerService.post_journal(
            journal_type=JournalType.PURCHASE,
            reference="tx-1",
            entries=[
                EntrySpec(wallet_account, Decimal("-300")),
                EntrySpec(aggregator_account, Decimal("285")),
                EntrySpec(revenue_account, Decimal("15")),
            ],
        )
        assert wallet_account.balance() == Decimal("700")
        assert revenue_account.balance() == Decimal("15")

    def test_balance_after_reversal(self, wallet_account, aggregator_account, revenue_account):
        # Post a purchase
        original = LedgerService.post_journal(
            journal_type=JournalType.PURCHASE,
            reference="tx-rev-1",
            entries=[
                EntrySpec(wallet_account, Decimal("-500")),
                EntrySpec(aggregator_account, Decimal("475")),
                EntrySpec(revenue_account, Decimal("25")),
            ],
        )
        assert wallet_account.balance() == Decimal("-500")

        # Reverse it (e.g. aggregator failed)
        LedgerService.reverse_journal(original, reference="tx-rev-1-reversal")

        assert wallet_account.balance() == Decimal("0")
        assert aggregator_account.balance() == Decimal("0")
        assert revenue_account.balance() == Decimal("0")


@pytest.mark.django_db
class TestImmutability:
    def test_cannot_update_entry(self, wallet_account, revenue_account):
        journal = LedgerService.post_journal(
            journal_type=JournalType.PURCHASE,
            reference="im-1",
            entries=[
                EntrySpec(wallet_account, Decimal("-100")),
                EntrySpec(revenue_account, Decimal("100")),
            ],
        )
        entry = journal.entries.first()
        entry.amount = Decimal("999")  # try to mutate
        with pytest.raises(ValueError, match="immutable"):
            entry.save()

    def test_cannot_delete_entry(self, wallet_account, revenue_account):
        journal = LedgerService.post_journal(
            journal_type=JournalType.PURCHASE,
            reference="im-2",
            entries=[
                EntrySpec(wallet_account, Decimal("-100")),
                EntrySpec(revenue_account, Decimal("100")),
            ],
        )
        entry = journal.entries.first()
        with pytest.raises(ValueError, match="cannot be deleted"):
            entry.delete()


@pytest.mark.django_db
class TestReversal:
    def test_reversal_creates_mirror_entries(self, wallet_account, aggregator_account, revenue_account):
        original = LedgerService.post_journal(
            journal_type=JournalType.PURCHASE,
            reference="rev-orig",
            entries=[
                EntrySpec(wallet_account, Decimal("-500"), "buy airtime"),
                EntrySpec(aggregator_account, Decimal("475"), "cost of goods"),
                EntrySpec(revenue_account, Decimal("25"), "our margin"),
            ],
        )

        reversal = LedgerService.reverse_journal(original, reference="rev-1")

        assert reversal.reverses_id == original.id
        assert reversal.journal_type == JournalType.REVERSAL
        assert reversal.entries.count() == 3

        # Sum of all entries (original + reversal) = 0 for each account
        for acc in [wallet_account, aggregator_account, revenue_account]:
            assert acc.balance() == Decimal("0")

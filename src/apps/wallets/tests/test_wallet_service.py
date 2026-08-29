"""
Tests for WalletService.

Includes concurrency tests that prove the same wallet can't be
double-spent under contention.
"""
import threading
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import connection

from apps.ledger.models import Account, AccountType, JournalType
from apps.ledger.services import EntrySpec
from apps.wallets.models import Wallet, WalletStatus
from apps.wallets.services import (
    InsufficientFundsError,
    InvalidAmountError,
    WalletNotTransactableError,
    WalletService,
)

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(phone_number="08011111111", password="p")


@pytest.fixture
def wallet(user):
    # Auto-created via signal, but call service to be safe
    return WalletService.create_wallet_for_user(user)


@pytest.fixture
def aggregator_account(db):
    return Account.objects.create(
        account_type=AccountType.AGGREGATOR_FLOAT,
        code="aggregator_float:test",
        name="Test aggregator",
    )


@pytest.fixture
def revenue_account(db):
    return Account.objects.create(
        account_type=AccountType.PLATFORM_REVENUE,
        code="platform_revenue:test",
        name="Test revenue",
    )


@pytest.fixture
def settlement_account(db):
    return Account.objects.create(
        account_type=AccountType.PENDING_SETTLEMENT,
        code="pending_settlement:test",
        name="Test settlement",
    )


@pytest.mark.django_db
class TestWalletProvisioning:
    def test_signal_creates_wallet_on_user_creation(self, db):
        user = User.objects.create_user(phone_number="08022222222", password="p")
        assert Wallet.objects.filter(user=user).exists()

    def test_create_wallet_is_idempotent(self, user):
        w1 = WalletService.create_wallet_for_user(user)
        w2 = WalletService.create_wallet_for_user(user)
        assert w1.pk == w2.pk

    def test_new_wallet_balance_is_zero(self, wallet):
        assert wallet.balance == Decimal("0")

    def test_wallet_default_status_active(self, wallet):
        assert wallet.status == WalletStatus.ACTIVE
        assert wallet.is_transactable is True


@pytest.mark.django_db
class TestCredit:
    def test_credit_increases_balance(self, wallet, settlement_account):
        WalletService.credit(
            wallet,
            amount=Decimal("1000"),
            source_account=settlement_account,
            reference="fund-1",
        )
        wallet.refresh_from_db()
        assert wallet.balance == Decimal("1000")

    def test_credit_zero_amount_rejected(self, wallet, settlement_account):
        with pytest.raises(InvalidAmountError):
            WalletService.credit(
                wallet,
                amount=Decimal("0"),
                source_account=settlement_account,
                reference="fund-x",
            )

    def test_credit_negative_amount_rejected(self, wallet, settlement_account):
        with pytest.raises(InvalidAmountError):
            WalletService.credit(
                wallet,
                amount=Decimal("-100"),
                source_account=settlement_account,
                reference="fund-y",
            )

    def test_suspended_wallet_rejects_credit(self, wallet, settlement_account):
        wallet.status = WalletStatus.SUSPENDED
        wallet.save()
        with pytest.raises(WalletNotTransactableError):
            WalletService.credit(
                wallet,
                amount=Decimal("100"),
                source_account=settlement_account,
                reference="fund-z",
            )


@pytest.mark.django_db
class TestDebit:
    def test_debit_decreases_balance(self, wallet, settlement_account, aggregator_account):
        WalletService.credit(
            wallet, amount=Decimal("1000"),
            source_account=settlement_account, reference="f-1",
        )
        WalletService.debit(
            wallet, amount=Decimal("300"),
            counterpart_account=aggregator_account, reference="d-1",
        )
        assert wallet.balance == Decimal("700")

    def test_debit_more_than_balance_fails(self, wallet, aggregator_account):
        with pytest.raises(InsufficientFundsError):
            WalletService.debit(
                wallet, amount=Decimal("100"),
                counterpart_account=aggregator_account, reference="d-x",
            )

    def test_frozen_wallet_rejects_debit(self, wallet, settlement_account, aggregator_account):
        WalletService.credit(
            wallet, amount=Decimal("1000"),
            source_account=settlement_account, reference="f-2",
        )
        wallet.status = WalletStatus.FROZEN
        wallet.save()
        with pytest.raises(WalletNotTransactableError):
            WalletService.debit(
                wallet, amount=Decimal("100"),
                counterpart_account=aggregator_account, reference="d-y",
            )

    def test_debit_with_split_credits_multiple_accounts(
        self, wallet, settlement_account, aggregator_account, revenue_account,
    ):
        WalletService.credit(
            wallet, amount=Decimal("1000"),
            source_account=settlement_account, reference="f-3",
        )
        WalletService.debit_with_split(
            wallet,
            total_amount=Decimal("500"),
            entries=[
                EntrySpec(aggregator_account, Decimal("475"), "cost"),
                EntrySpec(revenue_account, Decimal("25"), "margin"),
            ],
            reference="d-split-1",
        )
        assert wallet.balance == Decimal("500")
        assert aggregator_account.balance() == Decimal("475")
        assert revenue_account.balance() == Decimal("25")


@pytest.mark.django_db(transaction=True)
class TestConcurrentDebit:
    """
    The most important test in the whole codebase.

    If this fails, users can double-spend and money will disappear.
    """

    def test_concurrent_debits_do_not_double_spend(
        self, user, aggregator_account, settlement_account,
    ):
        """
        Fund a wallet with ₦100. Try to debit ₦100 twice concurrently
        from two threads. Exactly ONE should succeed; the other must fail
        with InsufficientFundsError.
        """
        wallet = WalletService.create_wallet_for_user(user)
        WalletService.credit(
            wallet, amount=Decimal("100"),
            source_account=settlement_account, reference="fund-conc",
        )

        errors: list[Exception] = []
        successes: list[str] = []

        def attempt_debit(ref: str) -> None:
            try:
                WalletService.debit(
                    wallet, amount=Decimal("100"),
                    counterpart_account=aggregator_account, reference=ref,
                )
                successes.append(ref)
            except InsufficientFundsError as e:
                errors.append(e)
            finally:
                connection.close()  # each thread must close its connection

        t1 = threading.Thread(target=attempt_debit, args=("d-conc-1",))
        t2 = threading.Thread(target=attempt_debit, args=("d-conc-2",))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Exactly one debit succeeded, one failed
        assert len(successes) == 1, f"Expected 1 success, got {len(successes)}"
        assert len(errors) == 1, f"Expected 1 InsufficientFundsError, got {len(errors)}"

        # Final balance must be exactly 0 (not negative!)
        wallet.refresh_from_db()
        assert wallet.balance == Decimal("0")

    def test_concurrent_credits_all_apply(
        self, user, settlement_account,
    ):
        """
        Two concurrent credits both apply. The wallet ends with the sum.
        """
        wallet = WalletService.create_wallet_for_user(user)

        def do_credit(ref: str, amount: str) -> None:
            try:
                WalletService.credit(
                    wallet, amount=Decimal(amount),
                    source_account=settlement_account, reference=ref,
                )
            finally:
                connection.close()

        t1 = threading.Thread(target=do_credit, args=("c-1", "100"))
        t2 = threading.Thread(target=do_credit, args=("c-2", "200"))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        wallet.refresh_from_db()
        assert wallet.balance == Decimal("300")


@pytest.mark.django_db
class TestIdempotency:
    def test_same_reference_replay_does_not_double_charge(
        self, wallet, settlement_account, aggregator_account,
    ):
        """A retried debit with the same reference must NOT double-charge."""
        WalletService.credit(
            wallet, amount=Decimal("1000"),
            source_account=settlement_account, reference="f-idem",
        )
        WalletService.debit(
            wallet, amount=Decimal("300"),
            counterpart_account=aggregator_account, reference="d-idem-1",
        )
        assert wallet.balance == Decimal("700")

        # Retry with same reference — must raise, wallet unchanged
        from apps.ledger.services import DuplicateJournalError
        with pytest.raises(DuplicateJournalError):
            WalletService.debit(
                wallet, amount=Decimal("300"),
                counterpart_account=aggregator_account, reference="d-idem-1",
            )
        assert wallet.balance == Decimal("700")

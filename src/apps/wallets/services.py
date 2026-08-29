"""
WalletService — atomic, race-safe debit/credit operations on wallets.

Uses:
  - SELECT FOR UPDATE row-locking to prevent concurrent double-spends
  - LedgerService for the actual accounting entries
  - Idempotency keys via the underlying journal reference

RULE: All wallet mutations MUST go through this service. Never write
      to the ledger directly for wallet operations.
"""
from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from apps.ledger.models import Account, AccountType, JournalType
from apps.ledger.services import EntrySpec, LedgerService

from .models import Wallet, WalletStatus


class WalletError(Exception):
    """Base wallet error."""


class InsufficientFundsError(WalletError):
    """Wallet balance would go negative after this operation."""


class WalletNotTransactableError(WalletError):
    """Wallet is frozen or suspended."""


class InvalidAmountError(WalletError):
    """Amount is not positive."""


class WalletService:
    """
    All wallet money moves go through here.

    Every method:
      - Wraps in an atomic transaction
      - Locks the wallet row with SELECT FOR UPDATE
      - Uses an idempotency key (reference) so retries don't double-charge
    """

    # ---------------------------------------------------------------- Setup

    @staticmethod
    @transaction.atomic
    def create_wallet_for_user(user) -> Wallet:
        """
        Provision a new wallet + its ledger account for a user.
        Idempotent: returns existing wallet if one already exists.
        """
        existing = Wallet.objects.filter(user=user).first()
        if existing:
            return existing

        account = Account.objects.create(
            account_type=AccountType.USER_WALLET,
            code=f"user_wallet:{user.public_id}",
            name=f"Wallet for {user.phone_number}",
            owner=user,
            currency="NGN",
        )
        return Wallet.objects.create(user=user, account=account)

    # ---------------------------------------------------------------- Debit

    @staticmethod
    @transaction.atomic
    def debit(
        wallet: Wallet,
        *,
        amount: Decimal | int | str,
        counterpart_account: Account,
        reference: str,
        journal_type: JournalType | str = JournalType.PURCHASE,
        description: str = "",
    ):
        """
        Move `amount` OUT of the wallet, INTO `counterpart_account`.

        Args:
            wallet: The wallet being debited.
            amount: Positive amount to debit. Must be > 0.
            counterpart_account: Ledger account that receives the amount
                (e.g. aggregator float when buying airtime).
            reference: Unique per journal_type (idempotency).
            journal_type: Defaults to PURCHASE.
            description: Human description.

        Raises:
            InvalidAmountError
            WalletNotTransactableError
            InsufficientFundsError
            DuplicateJournalError (from LedgerService) if reference reused.

        Returns:
            The created Journal.
        """
        amount = _coerce_positive(amount)

        # SELECT FOR UPDATE locks the wallet row — no other transaction
        # can debit this wallet until we commit.
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

        if not wallet.is_transactable:
            raise WalletNotTransactableError(
                f"Wallet {wallet.public_id} is {wallet.status}"
            )

        current = wallet.balance
        if current < amount:
            raise InsufficientFundsError(
                f"Balance {current} < requested debit {amount}"
            )

        return LedgerService.post_journal(
            journal_type=journal_type,
            reference=reference,
            description=description,
            entries=[
                EntrySpec(wallet.account, -amount, description),
                EntrySpec(counterpart_account, amount, description),
            ],
        )

    # ---------------------------------------------------------------- Credit

    @staticmethod
    @transaction.atomic
    def credit(
        wallet: Wallet,
        *,
        amount: Decimal | int | str,
        source_account: Account,
        reference: str,
        journal_type: JournalType | str = JournalType.FUNDING,
        description: str = "",
    ):
        """
        Move `amount` INTO the wallet FROM `source_account`.

        Args:
            wallet: The wallet being credited.
            amount: Positive amount to credit. Must be > 0.
            source_account: Ledger account that provides the amount
                (e.g. pending_settlement when Monnify webhook fires).
            reference: Unique per journal_type (idempotency).
            journal_type: Defaults to FUNDING.
            description: Human description.
        """
        amount = _coerce_positive(amount)

        # Even for credits we lock the row — keeps the whole event serialized
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

        # Suspended wallets can't receive money either (funds would be stuck)
        if wallet.status == WalletStatus.SUSPENDED:
            raise WalletNotTransactableError(
                f"Wallet {wallet.public_id} is suspended"
            )

        return LedgerService.post_journal(
            journal_type=journal_type,
            reference=reference,
            description=description,
            entries=[
                EntrySpec(wallet.account, amount, description),
                EntrySpec(source_account, -amount, description),
            ],
        )

    # ---------------------------------------------------------------- Multi-leg

    @staticmethod
    @transaction.atomic
    def debit_with_split(
        wallet: Wallet,
        *,
        total_amount: Decimal | int | str,
        entries: list[EntrySpec],
        reference: str,
        journal_type: JournalType | str = JournalType.PURCHASE,
        description: str = "",
    ):
        """
        Debit the wallet by `total_amount` and split the credit across
        multiple counterpart accounts (e.g. buying airtime splits between
        aggregator cost and platform revenue).

        Caller passes the counterpart entries only (positive amounts);
        the wallet debit is added automatically.

        Sum of `entries` must equal `total_amount`.
        """
        total_amount = _coerce_positive(total_amount)
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

        if not wallet.is_transactable:
            raise WalletNotTransactableError(
                f"Wallet {wallet.public_id} is {wallet.status}"
            )

        if wallet.balance < total_amount:
            raise InsufficientFundsError(
                f"Balance {wallet.balance} < requested debit {total_amount}"
            )

        # Sanity check that counterpart entries sum to total_amount
        counter_sum = sum((e.amount for e in entries), start=Decimal("0"))
        if counter_sum != total_amount:
            raise WalletError(
                f"Sum of counterpart entries ({counter_sum}) "
                f"must equal total_amount ({total_amount})"
            )

        all_entries = [
            EntrySpec(wallet.account, -total_amount, description),
            *entries,
        ]

        return LedgerService.post_journal(
            journal_type=journal_type,
            reference=reference,
            description=description,
            entries=all_entries,
        )


def _coerce_positive(amount) -> Decimal:
    """Coerce input to Decimal and ensure it's strictly positive."""
    d = amount if isinstance(amount, Decimal) else Decimal(str(amount))
    if d <= 0:
        raise InvalidAmountError(f"Amount must be > 0; got {d}")
    return d

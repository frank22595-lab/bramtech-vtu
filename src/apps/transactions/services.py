"""
TransactionService — the orchestrator.

Responsible for:
  1. Creating a Transaction with idempotency guard
  2. Debiting the user's wallet (split into aggregator float + platform revenue)
  3. Dispatching to the aggregator (via provider factory + routing)
  4. Recording the aggregator result on the transaction
  5. Refunding the wallet on failure
  6. Updating aggregator circuit breaker state

Every step is atomic. Failures don't leave inconsistent state.

Reference format: BRT-XXXXXX (external identifier shown to users)
"""
from __future__ import annotations

import secrets
from decimal import Decimal
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.aggregators.models import Aggregator
from apps.aggregators.providers.base import (
    DeliveryResult, DeliveryStatus, ProviderError, ProviderTimeoutError,
)
from apps.aggregators.services import (
    NoAvailableAggregatorError, get_provider, record_failure,
    record_success, select_route,
)
from apps.ledger.models import Account, AccountType
from apps.ledger.services import EntrySpec
from apps.services.models import ServiceCategory, ServiceVariation, VariationType
from apps.services.pricing import PriceQuote, get_price_for_user
from apps.wallets.models import Wallet
from apps.wallets.services import (
    InsufficientFundsError, WalletNotTransactableError, WalletService,
)

from .models import Transaction, TransactionStatus, TransactionType


class TransactionError(Exception):
    """Base transaction error."""


class DuplicateTransactionError(TransactionError):
    """Same (user, idempotency_key) submitted twice."""


class NoRouteError(TransactionError):
    """No aggregator available for this variation."""


# Map from ServiceCategory to TransactionType
_CATEGORY_TO_TYPE = {
    ServiceCategory.AIRTIME: TransactionType.AIRTIME,
    ServiceCategory.DATA: TransactionType.DATA,
    ServiceCategory.CABLE_TV: TransactionType.CABLE_TV,
    ServiceCategory.ELECTRICITY: TransactionType.ELECTRICITY,
    ServiceCategory.EDUCATION: TransactionType.EDUCATION,
    ServiceCategory.BETTING: TransactionType.BETTING,
}


def _new_reference() -> str:
    """Generate a human-readable transaction reference."""
    return f"BRT-{secrets.token_hex(6).upper()}"


class TransactionService:
    """
    All purchases go through initiate() -> which returns a Transaction.

    initiate() runs synchronously up through the debit; the actual aggregator
    dispatch happens via a Celery task (dispatch_transaction).
    """

    # ---------------- Initiation ----------------

    @staticmethod
    @transaction.atomic
    def initiate(
        *,
        user,
        variation: ServiceVariation,
        recipient: str,
        amount: Decimal | None = None,
        idempotency_key: str,
        recipient_meta: dict[str, Any] | None = None,
    ) -> Transaction:
        """
        Start a transaction.

        Steps (all atomic):
          1. Idempotency check (return existing Transaction if key already used)
          2. Compute pricing for user's tier
          3. Pick an aggregator (may raise NoRouteError)
          4. Create Transaction row (PENDING)
          5. Debit wallet with split entries (wallet -> aggregator float + revenue)
          6. Mark Transaction as PROCESSING
          7. Return the Transaction (caller enqueues dispatch task)
        """
        # 1. Idempotency
        existing = Transaction.objects.filter(
            user=user, idempotency_key=idempotency_key,
        ).first()
        if existing:
            return existing

        # 2. Pricing
        quote: PriceQuote = get_price_for_user(user, variation, amount=amount)

        # For FIXED variations, `amount` equals face value; for VARIABLE it's user-chosen
        if variation.variation_type == VariationType.FIXED:
            face_amount = variation.face_value or quote.sale_price
        else:
            face_amount = amount

        # 3. Pick aggregator
        try:
            aggregator, sku = select_route(variation)
        except NoAvailableAggregatorError as e:
            raise NoRouteError(str(e)) from e

        # 4. Create Transaction row
        tx_type = _CATEGORY_TO_TYPE.get(variation.service.category, TransactionType.OTHER)
        try:
            tx = Transaction.objects.create(
                reference=_new_reference(),
                user=user,
                transaction_type=tx_type,
                variation=variation,
                recipient=recipient,
                recipient_meta=recipient_meta or {},
                amount=face_amount,
                sale_price=quote.sale_price,
                cost_price=quote.cost_price,
                margin=quote.margin,
                idempotency_key=idempotency_key,
                aggregator=aggregator,
                status=TransactionStatus.PENDING,
            )
        except IntegrityError as e:
            raise DuplicateTransactionError(
                f"idempotency_key {idempotency_key} already used"
            ) from e

        # 5. Debit wallet — split into (aggregator_float, platform_revenue)
        wallet = Wallet.objects.select_for_update().get(user=user)
        agg_account = Account.objects.get(code=aggregator.ledger_account_code)
        revenue_account = _get_or_create_platform_revenue_account()

        try:
            debit_journal = WalletService.debit_with_split(
                wallet,
                total_amount=quote.sale_price,
                entries=[
                    EntrySpec(agg_account, quote.cost_price, f"cost:{tx.reference}"),
                    EntrySpec(revenue_account, quote.margin, f"margin:{tx.reference}"),
                ],
                reference=f"tx:{tx.reference}",
                description=f"{tx_type} to {recipient}",
            )
        except InsufficientFundsError:
            tx.status = TransactionStatus.FAILED
            tx.status_message = "Insufficient wallet balance"
            tx.completed_at = timezone.now()
            tx.save()
            raise
        except WalletNotTransactableError:
            tx.status = TransactionStatus.FAILED
            tx.status_message = "Wallet is not transactable"
            tx.completed_at = timezone.now()
            tx.save()
            raise

        # 6. Mark processing
        tx.debit_journal = debit_journal
        tx.status = TransactionStatus.PROCESSING
        tx.processing_at = timezone.now()
        tx.save(update_fields=["debit_journal", "status", "processing_at"])

        return tx

    # ---------------- Dispatch ----------------

    @staticmethod
    def dispatch(tx: Transaction) -> DeliveryResult:
        """
        Send the transaction to the aggregator.

        Called from a Celery task. NOT wrapped in a DB transaction because
        aggregator calls are I/O bound and can take seconds — we don't want
        to hold DB locks.
        """
        variation = tx.variation
        aggregator = tx.aggregator

        # Refresh SKU mapping in case admin changed something
        from apps.aggregators.models import AggregatorSKU
        try:
            sku = AggregatorSKU.objects.get(
                aggregator=aggregator, variation=variation, is_active=True,
            )
        except AggregatorSKU.DoesNotExist:
            TransactionService.mark_failed(tx, "SKU mapping missing for aggregator")
            return DeliveryResult(status=DeliveryStatus.FAILED, message="SKU missing")

        provider = get_provider(aggregator)

        tx.delivery_attempts += 1
        tx.last_attempt_at = timezone.now()
        tx.save(update_fields=["delivery_attempts", "last_attempt_at"])

        try:
            if tx.transaction_type == TransactionType.AIRTIME:
                result = provider.buy_airtime(
                    network=variation.service.network,
                    phone=tx.recipient,
                    amount=tx.amount,
                    reference=tx.reference,
                )
            elif tx.transaction_type == TransactionType.DATA:
                result = provider.buy_data(
                    network=variation.service.network,
                    phone=tx.recipient,
                    sku_code=sku.aggregator_sku_code,
                    reference=tx.reference,
                )
            elif tx.transaction_type == TransactionType.CABLE_TV:
                result = provider.buy_cable(
                    network=variation.service.network,
                    smartcard=tx.recipient,
                    sku_code=sku.aggregator_sku_code,
                    reference=tx.reference,
                )
            elif tx.transaction_type == TransactionType.ELECTRICITY:
                result = provider.buy_electricity(
                    disco=variation.service.network,
                    meter=tx.recipient,
                    amount=tx.amount,
                    meter_type=tx.recipient_meta.get("meter_type", "prepaid"),
                    reference=tx.reference,
                )
            else:
                result = DeliveryResult(
                    status=DeliveryStatus.FAILED,
                    message=f"Unsupported transaction type: {tx.transaction_type}",
                )
        except ProviderTimeoutError as e:
            # Unknown status — don't refund yet; reconciliation will figure it out
            result = DeliveryResult(status=DeliveryStatus.UNKNOWN, message=str(e))
        except ProviderError as e:
            result = DeliveryResult(status=DeliveryStatus.FAILED, message=str(e))
        except NotImplementedError as e:
            result = DeliveryResult(status=DeliveryStatus.FAILED, message=str(e))

        # Persist raw response
        tx.aggregator_reference = result.provider_reference
        tx.aggregator_response = result.raw_response
        tx.save(update_fields=["aggregator_reference", "aggregator_response"])

        # React to result
        if result.status == DeliveryStatus.SUCCESS:
            TransactionService.mark_success(tx, result.message)
            record_success(aggregator)
        elif result.status == DeliveryStatus.FAILED:
            TransactionService.mark_failed(tx, result.message)
            record_failure(aggregator)
        # PENDING or UNKNOWN: leave transaction as PROCESSING; reconciler will resolve

        return result

    # ---------------- Terminal transitions ----------------

    @staticmethod
    @transaction.atomic
    def mark_success(tx: Transaction, message: str = "") -> None:
        """Mark a transaction successful. Idempotent — safe to call twice."""
        tx = Transaction.objects.select_for_update().get(pk=tx.pk)
        if tx.is_terminal:
            return
        tx.status = TransactionStatus.SUCCESS
        tx.status_message = message or "Delivered"
        tx.completed_at = timezone.now()
        tx.save(update_fields=["status", "status_message", "completed_at"])

    @staticmethod
    @transaction.atomic
    def mark_failed(tx: Transaction, message: str = "") -> None:
        """
        Mark a transaction failed AND refund the wallet.
        Idempotent — safe to call twice.
        """
        tx = Transaction.objects.select_for_update().get(pk=tx.pk)
        if tx.is_terminal:
            return

        # Refund by reversing the debit journal
        if tx.debit_journal:
            from apps.ledger.services import LedgerService
            refund_ref = f"refund:{tx.reference}"
            # Check if refund already exists (idempotency)
            from apps.ledger.models import Journal, JournalType
            existing = Journal.objects.filter(
                journal_type=JournalType.REVERSAL, reference=refund_ref,
            ).first()
            if existing:
                tx.refund_journal = existing
            else:
                tx.refund_journal = LedgerService.reverse_journal(
                    tx.debit_journal, reference=refund_ref,
                    description=f"Refund for failed {tx.reference}",
                )

        tx.status = TransactionStatus.FAILED
        tx.status_message = message or "Delivery failed"
        tx.completed_at = timezone.now()
        tx.save(update_fields=["status", "status_message", "completed_at", "refund_journal"])


def _get_or_create_platform_revenue_account() -> Account:
    """Get (or lazily create) the main platform revenue account."""
    acc, _ = Account.objects.get_or_create(
        code="platform_revenue:main",
        defaults={
            "account_type": AccountType.PLATFORM_REVENUE,
            "name": "Platform revenue",
            "currency": "NGN",
        },
    )
    return acc

"""
Celery tasks for the transaction pipeline.

- dispatch_transaction: called right after initiate() to hit the aggregator async
- reconcile_stuck_transactions: periodic — checks PROCESSING transactions older
  than 90s and asks the aggregator for status; refunds if no answer after 5 min
- refund_sla_check: periodic — enforces the CBN 30-second refund SLA for
  transactions that failed but somehow didn't refund yet
"""
from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import Transaction, TransactionStatus
from .services import TransactionService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    ignore_result=True,
)
def dispatch_transaction(self, transaction_pk: int) -> str:
    """Send a transaction to its aggregator. Called from web request."""
    try:
        tx = Transaction.objects.get(pk=transaction_pk)
    except Transaction.DoesNotExist:
        logger.error("dispatch_transaction: no tx %s", transaction_pk)
        return "missing"

    if tx.is_terminal:
        return f"already {tx.status}"

    result = TransactionService.dispatch(tx)
    logger.info("dispatch_transaction %s -> %s", tx.reference, result.status.value)
    return result.status.value


@shared_task(ignore_result=True)
def reconcile_stuck_transactions() -> str:
    """
    Every 2 minutes: find PROCESSING transactions older than 90s.
    Query the aggregator for their real status. Resolve accordingly.

    If a transaction has been stuck > 5 minutes with no aggregator answer,
    auto-refund (assume delivery failed).
    """
    from apps.aggregators.services import get_provider

    cutoff_stale = timezone.now() - timedelta(seconds=90)
    hard_cutoff = timezone.now() - timedelta(minutes=5)

    stuck = Transaction.objects.filter(
        status=TransactionStatus.PROCESSING,
        processing_at__lt=cutoff_stale,
    ).select_related("aggregator")[:100]

    resolved = 0
    for tx in stuck:
        # Hard timeout — refund
        if tx.processing_at and tx.processing_at < hard_cutoff:
            TransactionService.mark_failed(tx, "Auto-refund: no aggregator response")
            resolved += 1
            continue

        # Query aggregator for real status
        if not tx.aggregator or not tx.aggregator_reference:
            continue

        try:
            provider = get_provider(tx.aggregator)
            result = provider.check_status(tx.aggregator_reference)
        except NotImplementedError:
            continue
        except Exception as e:
            logger.warning("reconcile: status check failed for %s: %s", tx.reference, e)
            continue

        from apps.aggregators.providers.base import DeliveryStatus
        if result.status == DeliveryStatus.SUCCESS:
            TransactionService.mark_success(tx, "Confirmed on reconciliation")
            resolved += 1
        elif result.status == DeliveryStatus.FAILED:
            TransactionService.mark_failed(tx, "Failed (reconciliation)")
            resolved += 1
        # PENDING/UNKNOWN: leave as-is, will re-check next cycle

    return f"reconciled: {resolved}/{len(stuck)}"


@shared_task(ignore_result=True)
def refund_sla_check() -> str:
    """
    Every minute: find transactions marked FAILED but with no refund_journal.
    (Should never happen if mark_failed is used correctly, but this is our
    safety net for the CBN 30-second SLA.)
    """
    to_refund = Transaction.objects.filter(
        status=TransactionStatus.FAILED, refund_journal__isnull=True,
        debit_journal__isnull=False,
    )[:100]

    count = 0
    for tx in to_refund:
        # Reset status so mark_failed will process it
        tx.status = TransactionStatus.PROCESSING
        tx.save(update_fields=["status"])
        TransactionService.mark_failed(tx, "SLA-triggered refund")
        count += 1
    return f"sla-refunded: {count}"

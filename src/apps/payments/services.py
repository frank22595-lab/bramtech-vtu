"""
Monnify integration.

Two responsibilities:
  1. Create dedicated virtual accounts for users (bank transfer funding)
  2. Handle incoming webhook events (SUCCESSFUL_TRANSACTION) and credit wallets

Uses ledger correctly:
  - Every funding creates a journal (credit user_wallet, debit pending_settlement)
  - Duplicate webhooks are rejected via WebhookInbox unique constraint
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import logging
from decimal import Decimal
from typing import Any

import httpx
from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.ledger.models import Account, AccountType
from apps.ledger.services import EntrySpec, LedgerService, JournalType
from apps.wallets.services import WalletService

from .models import (
    FundingEvent, FundingStatus, PaymentProvider,
    VirtualAccount, WebhookInbox,
)

logger = logging.getLogger(__name__)


class MonnifyError(Exception):
    pass


class WebhookAlreadyProcessed(Exception):
    pass


def _get_settlement_account() -> Account:
    """The account funds land in before being credited to the user wallet."""
    acc, _ = Account.objects.get_or_create(
        code="pending_settlement:monnify",
        defaults={
            "account_type": AccountType.PENDING_SETTLEMENT,
            "name": "Monnify settlement",
            "currency": "NGN",
        },
    )
    return acc


class MonnifyClient:
    """Thin Monnify API wrapper."""

    def __init__(self):
        self.api_key = getattr(settings, "MONNIFY_API_KEY", "")
        self.secret_key = getattr(settings, "MONNIFY_SECRET_KEY", "")
        self.contract_code = getattr(settings, "MONNIFY_CONTRACT_CODE", "")
        self.base_url = getattr(settings, "MONNIFY_BASE_URL", "https://sandbox.monnify.com")

    def _basic_auth(self) -> str:
        raw = f"{self.api_key}:{self.secret_key}".encode()
        return "Basic " + base64.b64encode(raw).decode()

    def _login(self) -> str:
        """Get an OAuth2 access token."""
        with httpx.Client(timeout=15.0) as c:
            r = c.post(
                f"{self.base_url}/api/v1/auth/login",
                headers={"Authorization": self._basic_auth()},
            )
        r.raise_for_status()
        data = r.json()
        return data["responseBody"]["accessToken"]

    def create_reserved_account(self, user) -> VirtualAccount:
        """Create a dedicated virtual account for the user."""
        token = self._login()
        payload = {
            "accountReference": f"user-{user.public_id}",
            "accountName": user.get_full_name() or user.phone_number,
            "currencyCode": "NGN",
            "contractCode": self.contract_code,
            "customerEmail": user.email or f"{user.phone_number.strip('+')}@bramtechvtu.com",
            "customerName": user.get_full_name() or user.phone_number,
            "getAllAvailableBanks": True,
        }
        with httpx.Client(timeout=20.0) as c:
            r = c.post(
                f"{self.base_url}/api/v2/bank-transfer/reserved-accounts",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )
        if r.status_code >= 300:
            raise MonnifyError(f"Monnify error {r.status_code}: {r.text}")

        body = r.json().get("responseBody", {})
        accounts = body.get("accounts", [])
        if not accounts:
            raise MonnifyError(f"No accounts returned: {body}")

        # Just take the first (usually Wema). Rest can be added later.
        first = accounts[0]
        va, _ = VirtualAccount.objects.update_or_create(
            user=user, account_number=first["accountNumber"],
            defaults={
                "provider": PaymentProvider.MONNIFY,
                "bank_name": first["bankName"],
                "account_name": payload["accountName"],
                "provider_reference": body.get("reservationReference", ""),
                "is_active": True,
            },
        )
        return va


def verify_monnify_signature(raw_body: bytes, signature_header: str) -> bool:
    """
    Monnify signs webhooks with HMAC-SHA512 using your secret key.

    The Header 'monnify-signature' contains a hex digest of the raw request body
    signed with your secret key.
    """
    secret = getattr(settings, "MONNIFY_SECRET_KEY", "")
    if not secret or not signature_header:
        return False
    expected = hmac.new(
        secret.encode(), raw_body, hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header.lower())


@transaction.atomic
def process_monnify_webhook(payload: dict[str, Any]) -> FundingEvent | None:
    """
    Process a verified Monnify webhook payload.

    Idempotent: same eventId is only processed once (WebhookInbox unique constraint).
    Returns the FundingEvent if applied, None if it wasn't relevant.
    """
    event_type = payload.get("eventType")
    event_data = payload.get("eventData") or {}
    event_id = str(payload.get("eventReference") or event_data.get("transactionReference") or "")

    # Log the webhook first (idempotency guard)
    try:
        WebhookInbox.objects.create(
            provider=PaymentProvider.MONNIFY,
            event_id=event_id,
            signature_verified=True,
            payload=payload,
        )
    except IntegrityError:
        raise WebhookAlreadyProcessed(event_id)

    # We only care about successful transactions
    if event_type != "SUCCESSFUL_TRANSACTION":
        return None

    # Find the user by the accountReference we set at creation time
    from django.contrib.auth import get_user_model
    User = get_user_model()

    account_reference = event_data.get("product", {}).get("reference") or ""
    # accountReference is "user-<public_id>"
    if not account_reference.startswith("user-"):
        logger.warning("Monnify webhook: unrecognized accountReference %r", account_reference)
        return None

    user_public_id = account_reference[len("user-"):]
    try:
        user = User.objects.get(public_id=user_public_id)
    except User.DoesNotExist:
        logger.error("Monnify webhook: no user for public_id=%s", user_public_id)
        return None

    amount = Decimal(str(event_data.get("amountPaid", "0")))
    fee = Decimal(str(event_data.get("totalPayable", amount))) - amount
    if fee < 0:
        fee = Decimal("0")
    net = amount  # We credit the user with what they actually paid, we absorb the fee separately

    provider_ref = str(event_data.get("transactionReference"))

    # Create the FundingEvent
    fe, created = FundingEvent.objects.get_or_create(
        provider=PaymentProvider.MONNIFY,
        provider_reference=provider_ref,
        defaults={
            "user": user,
            "amount": amount,
            "fee": fee,
            "net_amount": net,
            "raw_payload": payload,
            "status": FundingStatus.RECEIVED,
        },
    )
    if not created and fe.status == FundingStatus.APPLIED:
        # Already applied — nothing to do
        return fe

    # Credit the wallet
    from apps.wallets.models import Wallet
    wallet = Wallet.objects.select_for_update().get(user=user)
    settlement = _get_settlement_account()

    journal = WalletService.credit(
        wallet, amount=net,
        source_account=settlement,
        reference=f"fund:{provider_ref}",
        journal_type=JournalType.FUNDING,
        description=f"Bank funding via Monnify (ref {provider_ref})",
    )

    fe.status = FundingStatus.APPLIED
    fe.ledger_journal = journal
    fe.applied_at = timezone.now()
    fe.save(update_fields=["status", "ledger_journal", "applied_at"])
    return fe

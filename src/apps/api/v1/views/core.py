"""Wallet + services + purchase endpoints."""
from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.services.models import Service, ServiceCategory, ServiceVariation
from apps.transactions.models import Transaction
from apps.transactions.services import (
    DuplicateTransactionError, NoRouteError, TransactionService,
)
from apps.transactions.tasks import dispatch_transaction
from apps.wallets.models import Wallet
from apps.wallets.services import (
    InsufficientFundsError, WalletNotTransactableError,
)

from ..serializers.core import (
    PurchaseSerializer, ServiceSerializer,
    ServiceVariationSerializer, TransactionSerializer, WalletSerializer,
)


# ---------------- Wallet ----------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_wallet(request):
    """Get the current user's wallet + balance."""
    wallet = get_object_or_404(Wallet, user=request.user)
    return Response(WalletSerializer(wallet).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_virtual_accounts(request):
    """List the user's virtual accounts for funding."""
    accounts = request.user.virtual_accounts.filter(is_active=True)
    return Response([
        {
            "account_number": a.account_number,
            "bank_name": a.bank_name,
            "account_name": a.account_name,
        } for a in accounts
    ])


# ---------------- Services catalog ----------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_services(request):
    """List active services, optionally filtered by category."""
    qs = Service.objects.filter(is_active=True)
    category = request.query_params.get("category")
    if category:
        qs = qs.filter(category=category)
    return Response(ServiceSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_variations(request, service_slug):
    """List active variations for a service, priced for the current user."""
    service = get_object_or_404(Service, slug=service_slug, is_active=True)
    variations = service.variations.filter(is_active=True)
    serializer = ServiceVariationSerializer(
        variations, many=True, context={"request": request},
    )
    return Response(serializer.data)


# ---------------- Purchase ----------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase(request):
    """
    Buy a service.

    Body: {variation_id, recipient, amount?, pin, idempotency_key, recipient_meta?}
    Returns: transaction details (PROCESSING initially, poll for status).
    """
    serializer = PurchaseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    # Check PIN
    user = request.user
    if user.is_pin_locked():
        return Response(
            {"detail": "Transaction PIN is temporarily locked"},
            status=status.HTTP_423_LOCKED,
        )
    if not user.transaction_pin_hash:
        return Response(
            {"detail": "Set a transaction PIN first"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not user.check_transaction_pin(data["pin"]):
        return Response(
            {"detail": "Invalid transaction PIN"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Resolve the variation
    variation = get_object_or_404(
        ServiceVariation, public_id=data["variation_id"], is_active=True,
    )

    try:
        tx = TransactionService.initiate(
            user=user,
            variation=variation,
            recipient=data["recipient"],
            amount=data.get("amount"),
            idempotency_key=data["idempotency_key"],
            recipient_meta=data.get("recipient_meta") or {},
        )
    except NoRouteError:
        return Response(
            {"detail": "Service temporarily unavailable — no route"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except InsufficientFundsError:
        return Response(
            {"detail": "Insufficient wallet balance"},
            status=status.HTTP_402_PAYMENT_REQUIRED,
        )
    except WalletNotTransactableError:
        return Response(
            {"detail": "Wallet is frozen or suspended"},
            status=status.HTTP_403_FORBIDDEN,
        )
    except DuplicateTransactionError:
        # Idempotency: return existing tx (initiate handles this internally now, but safety)
        tx = Transaction.objects.get(
            user=user, idempotency_key=data["idempotency_key"],
        )

    # Dispatch async (returns immediately)
    dispatch_transaction.delay(tx.pk)

    return Response(TransactionSerializer(tx).data, status=status.HTTP_202_ACCEPTED)


# ---------------- Transaction history ----------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_transactions(request):
    """
    Paginated transaction history for the current user.
    Query params: ?status=&type=&limit=&offset=
    """
    qs = Transaction.objects.filter(user=request.user).order_by("-created_at")

    status_filter = request.query_params.get("status")
    if status_filter:
        qs = qs.filter(status=status_filter)

    type_filter = request.query_params.get("type")
    if type_filter:
        qs = qs.filter(transaction_type=type_filter)

    # Manual light pagination
    try:
        limit = min(int(request.query_params.get("limit", 20)), 100)
        offset = int(request.query_params.get("offset", 0))
    except ValueError:
        limit, offset = 20, 0

    total = qs.count()
    items = qs[offset:offset + limit]

    return Response({
        "count": total,
        "limit": limit,
        "offset": offset,
        "results": TransactionSerializer(items, many=True).data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transaction_detail(request, reference):
    """Get a single transaction by reference."""
    tx = get_object_or_404(Transaction, reference=reference, user=request.user)
    return Response(TransactionSerializer(tx).data)

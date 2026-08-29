"""Wallet, services, transactions serializers."""
from rest_framework import serializers

from apps.services.models import Service, ServiceVariation, TieredPricing
from apps.transactions.models import Transaction
from apps.wallets.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = ("public_id", "balance", "status", "created_at")
        read_only_fields = fields

    def get_balance(self, obj):
        return str(obj.balance)


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "public_id", "category", "network", "name", "slug",
            "description", "display_order", "icon",
        )


class ServiceVariationSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    network = serializers.CharField(source="service.network", read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = ServiceVariation
        fields = (
            "public_id", "service_name", "network", "name",
            "variation_type", "variation_code", "face_value",
            "validity_days", "data_mb", "display_order", "price",
        )

    def get_price(self, obj):
        """Return the price for the CURRENT authenticated user's tier."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            # Fall back to regular pricing
            row = obj.pricing.filter(user_tier="regular", is_active=True).first()
            if row and row.sale_price:
                return str(row.sale_price)
            return None
        try:
            from apps.services.pricing import get_pricing_row
            row = get_pricing_row(obj, request.user.tier)
            if row.sale_price:
                return str(row.sale_price)
            return None
        except Exception:
            return None


class TransactionSerializer(serializers.ModelSerializer):
    variation_name = serializers.CharField(source="variation.name", read_only=True)
    network = serializers.CharField(source="variation.service.network", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "public_id", "reference", "transaction_type", "variation_name",
            "network", "recipient", "amount", "sale_price",
            "status", "status_message", "created_at", "completed_at",
        )
        read_only_fields = fields


class PurchaseSerializer(serializers.Serializer):
    """
    Generic purchase endpoint payload.

    Client sends the variation public_id + recipient + optional amount
    (for VARIABLE_AMOUNT variations like airtime) + a transaction PIN.
    """
    variation_id = serializers.UUIDField()
    recipient = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True,
    )
    pin = serializers.CharField(min_length=4, max_length=6, write_only=True)
    idempotency_key = serializers.CharField(max_length=100)
    recipient_meta = serializers.DictField(required=False, default=dict)

from django.contrib import admin
from django.utils.html import format_html

from .models import Transaction, TransactionStatus


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference", "user", "transaction_type", "variation",
        "recipient", "sale_price", "status_display", "created_at",
    )
    list_filter = ("status", "transaction_type", "aggregator", "created_at")
    search_fields = (
        "reference", "user__phone_number", "recipient",
        "aggregator_reference", "idempotency_key",
    )
    readonly_fields = (
        "public_id", "reference", "user", "variation", "recipient",
        "recipient_meta", "amount", "sale_price", "cost_price", "margin",
        "idempotency_key", "aggregator", "aggregator_reference",
        "aggregator_response", "debit_journal", "refund_journal",
        "created_at", "processing_at", "completed_at",
        "delivery_attempts", "last_attempt_at",
    )
    fieldsets = (
        ("Reference", {"fields": ("public_id", "reference", "user", "status", "status_message")}),
        ("Service", {"fields": ("transaction_type", "variation", "recipient", "recipient_meta")}),
        ("Money", {"fields": ("amount", "sale_price", "cost_price", "margin")}),
        ("Idempotency", {"fields": ("idempotency_key",)}),
        ("Aggregator", {"fields": ("aggregator", "aggregator_reference", "aggregator_response",
                                    "delivery_attempts", "last_attempt_at")}),
        ("Ledger", {"fields": ("debit_journal", "refund_journal")}),
        ("Timestamps", {"fields": ("created_at", "processing_at", "completed_at")}),
    )

    @admin.display(description="Status")
    def status_display(self, obj: Transaction) -> str:
        color = {
            TransactionStatus.PENDING: "gray",
            TransactionStatus.PROCESSING: "orange",
            TransactionStatus.SUCCESS: "green",
            TransactionStatus.FAILED: "red",
            TransactionStatus.REFUNDED: "purple",
        }.get(obj.status, "black")
        return format_html('<b style="color:{};">{}</b>', color, obj.get_status_display())

    def has_add_permission(self, request) -> bool:
        return False  # Transactions are created via TransactionService only

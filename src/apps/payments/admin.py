from django.contrib import admin

from .models import FundingEvent, VirtualAccount, WebhookInbox


@admin.register(VirtualAccount)
class VirtualAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "account_number", "bank_name", "provider", "is_active")
    list_filter = ("provider", "bank_name", "is_active")
    search_fields = ("account_number", "user__phone_number", "user__email")


@admin.register(FundingEvent)
class FundingEventAdmin(admin.ModelAdmin):
    list_display = (
        "provider_reference", "user", "amount", "status",
        "applied_at", "created_at",
    )
    list_filter = ("provider", "status", "created_at")
    search_fields = ("provider_reference", "user__phone_number")
    readonly_fields = (
        "public_id", "user", "provider", "provider_reference",
        "amount", "fee", "net_amount", "raw_payload",
        "ledger_journal", "created_at", "applied_at",
    )


@admin.register(WebhookInbox)
class WebhookInboxAdmin(admin.ModelAdmin):
    list_display = ("provider", "event_id", "signature_verified",
                     "processed_at", "received_at")
    list_filter = ("provider", "signature_verified")
    search_fields = ("event_id",)
    readonly_fields = ("provider", "event_id", "signature_verified",
                        "payload", "received_at", "processed_at", "processing_error")

    def has_add_permission(self, request) -> bool:
        return False

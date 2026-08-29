from django.contrib import admin
from django.utils.html import format_html

from .models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance_display", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__phone_number", "user__email", "account__code")
    readonly_fields = ("public_id", "account", "created_at", "updated_at", "balance_display")
    fieldsets = (
        (None, {"fields": ("public_id", "user", "account", "balance_display")}),
        ("Status", {"fields": ("status", "frozen_reason", "frozen_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Balance (NGN)")
    def balance_display(self, obj: Wallet) -> str:
        bal = obj.balance
        color = "green" if bal >= 0 else "red"
        return format_html('<b style="color:{};">₦{}</b>', color, f"{bal:,.2f}")

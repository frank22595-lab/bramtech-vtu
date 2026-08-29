from django.contrib import admin
from django.utils.html import format_html

from .models import Account, Journal, LedgerEntry


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("code", "account_type", "owner", "currency", "current_balance", "is_active")
    list_filter = ("account_type", "currency", "is_active")
    search_fields = ("code", "name", "owner__phone_number", "owner__email")
    readonly_fields = ("public_id", "created_at")

    @admin.display(description="Balance")
    def current_balance(self, obj: Account) -> str:
        bal = obj.balance()
        color = "green" if bal >= 0 else "red"
        return format_html('<b style="color:{};">{} {}</b>', color, obj.currency, f"{bal:,.2f}")


class LedgerEntryInline(admin.TabularInline):
    model = LedgerEntry
    extra = 0
    can_delete = False
    readonly_fields = ("account", "amount", "currency", "description", "created_at")

    def has_add_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ("reference", "journal_type", "created_at", "balanced_display")
    list_filter = ("journal_type", "created_at")
    search_fields = ("reference", "description")
    readonly_fields = ("public_id", "created_at", "reverses")
    inlines = [LedgerEntryInline]

    @admin.display(description="Balanced?", boolean=True)
    def balanced_display(self, obj: Journal) -> bool:
        return obj.is_balanced()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("account", "amount", "currency", "journal", "created_at")
    list_filter = ("currency", "created_at")
    search_fields = ("account__code", "journal__reference", "description")
    readonly_fields = ("public_id", "journal", "account", "amount", "currency", "description", "created_at")

    def has_add_permission(self, request) -> bool:
        return False  # Only create via LedgerService

    def has_change_permission(self, request, obj=None) -> bool:
        return False  # Ledger entries are immutable

    def has_delete_permission(self, request, obj=None) -> bool:
        return False  # Never delete

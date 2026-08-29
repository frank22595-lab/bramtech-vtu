from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Aggregator, AggregatorHealth, AggregatorRoute, AggregatorSKU,
    CircuitState,
)


@admin.register(Aggregator)
class AggregatorAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "status", "ledger_account_code", "created_at")
    list_filter = ("status",)
    search_fields = ("code", "name")


@admin.register(AggregatorSKU)
class AggregatorSKUAdmin(admin.ModelAdmin):
    list_display = ("aggregator", "variation", "aggregator_sku_code", "is_active")
    list_filter = ("aggregator", "is_active")
    search_fields = ("aggregator_sku_code", "variation__name")


@admin.register(AggregatorRoute)
class AggregatorRouteAdmin(admin.ModelAdmin):
    list_display = ("variation", "aggregator", "priority", "is_active")
    list_filter = ("aggregator", "is_active")
    search_fields = ("variation__name", "aggregator__code")
    ordering = ("variation", "priority")


@admin.register(AggregatorHealth)
class AggregatorHealthAdmin(admin.ModelAdmin):
    list_display = (
        "aggregator", "state_display", "consecutive_failures",
        "consecutive_successes", "last_success_at", "last_failure_at",
    )
    list_filter = ("state",)
    readonly_fields = (
        "consecutive_failures", "consecutive_successes",
        "last_failure_at", "last_success_at", "open_until", "updated_at",
    )

    @admin.display(description="State")
    def state_display(self, obj: AggregatorHealth) -> str:
        color = {
            CircuitState.CLOSED: "green",
            CircuitState.HALF_OPEN: "orange",
            CircuitState.OPEN: "red",
        }.get(obj.state, "gray")
        return format_html('<b style="color:{};">{}</b>', color, obj.get_state_display())

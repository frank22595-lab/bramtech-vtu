from django.contrib import admin
from django.utils.html import format_html

from .models import Service, ServiceVariation, TieredPricing


class TieredPricingInline(admin.TabularInline):
    model = TieredPricing
    extra = 5  # allow all 5 tiers by default
    fields = ("user_tier", "cost_price", "sale_price", "discount_percent", "is_active")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "network", "is_active", "display_order")
    list_filter = ("category", "network", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ServiceVariation)
class ServiceVariationAdmin(admin.ModelAdmin):
    list_display = (
        "name", "service", "variation_type", "face_value",
        "variation_code", "is_active",
    )
    list_filter = ("variation_type", "service__category", "service__network", "is_active")
    search_fields = ("name", "variation_code", "service__name")
    inlines = [TieredPricingInline]


@admin.register(TieredPricing)
class TieredPricingAdmin(admin.ModelAdmin):
    list_display = (
        "variation", "user_tier", "cost_price", "sale_price",
        "discount_percent", "margin_display", "is_active",
    )
    list_filter = ("user_tier", "is_active", "variation__service__category")
    search_fields = ("variation__name", "variation__service__name")

    @admin.display(description="Margin")
    def margin_display(self, obj: TieredPricing) -> str:
        if obj.variation.is_variable:
            return "—"
        try:
            m = obj.margin()
            color = "green" if m > 0 else "red"
            return format_html('<b style="color:{};">₦{:.2f}</b>', color, m)
        except Exception:
            return "—"

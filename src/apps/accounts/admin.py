from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin configuration for the custom User model."""

    ordering = ("-date_joined",)
    list_display = (
        "phone_number",
        "email",
        "get_full_name",
        "tier",
        "kyc_tier",
        "is_active",
        "date_joined",
    )
    list_filter = ("tier", "kyc_tier", "is_active", "is_staff", "phone_verified", "email_verified")
    search_fields = ("phone_number", "email", "first_name", "last_name", "referral_code")

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Verification"), {
            "fields": ("phone_verified", "email_verified", "nin_verified_at", "bvn_verified_at"),
        }),
        (_("Business"), {
            "fields": ("tier", "tier_upgraded_at", "kyc_tier", "referral_code", "referred_by"),
        }),
        (_("OTP preferences"), {
            "fields": ("prefer_whatsapp_otp", "whatsapp_opted_in", "telegram_chat_id"),
            "classes": ("collapse",),
        }),
        (_("Security"), {
            "fields": ("transaction_pin_hash", "pin_attempts", "pin_locked_until", "last_login_ip"),
            "classes": ("collapse",),
        }),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            "classes": ("collapse",),
        }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "email", "password1", "password2"),
        }),
    )

    readonly_fields = (
        "date_joined",
        "last_login",
        "transaction_pin_hash",
        "referral_code",
        "public_id",
    )

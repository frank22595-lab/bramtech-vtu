"""
Custom User model for BramTech VTU.

Uses phone number as the primary identifier. Includes:
- KYC tier tracking (limits transaction volumes)
- Reseller tier (Bronze/Silver/Gold/Platinum for pricing)
- Transaction PIN (separate from login password)
- Referral tracking
"""
from __future__ import annotations

import re
import secrets
import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .managers import UserManager


# Nigerian phone number: +234 followed by 10 digits, OR 11 digits starting with 0
NG_PHONE_REGEX = re.compile(r"^(\+234|234|0)([789][01]\d{8})$")


def normalize_ng_phone(value: str) -> str:
    """
    Normalize Nigerian phone numbers to +234XXXXXXXXXX format.

    Accepts: 08012345678, 8012345678, 2348012345678, +2348012345678
    Returns: +2348012345678
    Raises ValidationError for anything else.
    """
    if not value:
        raise ValidationError("Phone number is required")

    # Strip spaces, dashes, parentheses
    cleaned = re.sub(r"[\s\-()]", "", value)

    match = NG_PHONE_REGEX.match(cleaned)
    if not match:
        raise ValidationError(
            "Enter a valid Nigerian phone number "
            "(e.g. 08012345678 or +2348012345678)"
        )

    # Rebuild in canonical +234 format
    return f"+234{match.group(2)}"


class KYCTier(models.IntegerChoices):
    """
    KYC tiers determine transaction limits.
    Tier 0 is default on registration (very limited).
    """
    TIER_0 = 0, "Unverified"           # Just phone verified
    TIER_1 = 1, "Basic (Email)"        # Email verified
    TIER_2 = 2, "Intermediate (NIN)"   # NIN verified
    TIER_3 = 3, "Full (BVN)"           # BVN verified


class UserTier(models.TextChoices):
    """
    Reseller/pricing tiers. Determines what price the user pays
    for services. Upgrade via one-time payment.
    """
    REGULAR = "regular", "Regular User"
    BRONZE = "bronze", "Bronze Reseller"
    SILVER = "silver", "Silver Reseller"
    GOLD = "gold", "Gold Reseller"
    PLATINUM = "platinum", "Platinum Reseller"


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model.

    Phone number is the primary identifier and username.
    Email is optional but strongly recommended.
    """

    # Unique identifier — never expose sequential IDs externally
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
    )

    # === Identity ===
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        help_text="Nigerian phone number in +234XXXXXXXXXX format",
    )
    email = models.EmailField(
        blank=True,
        null=True,
        unique=True,
        db_index=True,
        help_text="Optional but recommended for free OTP & recovery",
    )
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    # === Verification ===
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    # === KYC ===
    kyc_tier = models.IntegerField(
        choices=KYCTier.choices,
        default=KYCTier.TIER_0,
        db_index=True,
    )
    nin_verified_at = models.DateTimeField(null=True, blank=True)
    bvn_verified_at = models.DateTimeField(null=True, blank=True)

    # === Business tier (pricing) ===
    tier = models.CharField(
        max_length=20,
        choices=UserTier.choices,
        default=UserTier.REGULAR,
        db_index=True,
    )
    tier_upgraded_at = models.DateTimeField(null=True, blank=True)

    # === Transaction PIN (separate from login password) ===
    transaction_pin_hash = models.CharField(max_length=255, blank=True)
    pin_attempts = models.IntegerField(default=0)
    pin_locked_until = models.DateTimeField(null=True, blank=True)

    # === OTP delivery preferences ===
    prefer_whatsapp_otp = models.BooleanField(default=False)
    whatsapp_opted_in = models.BooleanField(default=False)
    telegram_chat_id = models.CharField(max_length=64, blank=True)

    # === Referral tracking ===
    referral_code = models.CharField(
        max_length=12,
        unique=True,
        db_index=True,
        blank=True,
    )
    referred_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referrals",
    )

    # === Django admin/auth flags ===
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # === Timestamps ===
    date_joined = models.DateTimeField(default=timezone.now)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS: list[str] = []  # only phone_number required for createsuperuser

    class Meta:
        db_table = "auth_user"
        verbose_name = "user"
        verbose_name_plural = "users"
        indexes = [
            models.Index(fields=["kyc_tier", "tier"]),
            models.Index(fields=["date_joined"]),
        ]

    def __str__(self) -> str:
        return f"{self.phone_number} ({self.get_full_name() or 'user'})"

    # ---------------- Normalisation ----------------

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Wrapper to expose phone normalization to the manager."""
        return normalize_ng_phone(phone)

    def clean(self) -> None:
        super().clean()
        if self.phone_number:
            self.phone_number = normalize_ng_phone(self.phone_number)
        if self.email:
            self.email = self.email.lower().strip()

    def save(self, *args, **kwargs) -> None:
        # Ensure normalization even if clean() wasn't called
        if self.phone_number:
            self.phone_number = normalize_ng_phone(self.phone_number)
        if self.email:
            self.email = self.email.lower().strip()

        # Auto-generate referral code on first save
        if not self.referral_code:
            self.referral_code = self._generate_referral_code()

        super().save(*args, **kwargs)

    def _generate_referral_code(self) -> str:
        """Generate a unique 8-char referral code."""
        for _ in range(10):
            code = secrets.token_urlsafe(6)[:8].upper().replace("-", "X").replace("_", "Y")
            if not User.objects.filter(referral_code=code).exists():
                return code
        # Extremely unlikely fallback
        return secrets.token_urlsafe(10)[:12].upper()

    # ---------------- Helpers ----------------

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name or self.phone_number

    # ---------------- Transaction PIN ----------------

    def set_transaction_pin(self, pin: str) -> None:
        """Hash and set the user's transaction PIN (4-6 digits)."""
        if not pin or not pin.isdigit() or not (4 <= len(pin) <= 6):
            raise ValidationError("Transaction PIN must be 4-6 digits")
        self.transaction_pin_hash = make_password(pin)
        self.pin_attempts = 0
        self.pin_locked_until = None

    def check_transaction_pin(self, pin: str) -> bool:
        """Verify a transaction PIN. Handles lockout on too many failures."""
        if self.is_pin_locked():
            return False
        if not self.transaction_pin_hash:
            return False

        is_valid = check_password(pin, self.transaction_pin_hash)
        if is_valid:
            self.pin_attempts = 0
            self.pin_locked_until = None
            self.save(update_fields=["pin_attempts", "pin_locked_until"])
        else:
            self.pin_attempts += 1
            if self.pin_attempts >= 5:
                # Lock for 15 minutes after 5 wrong attempts
                self.pin_locked_until = timezone.now() + timezone.timedelta(minutes=15)
            self.save(update_fields=["pin_attempts", "pin_locked_until"])
        return is_valid

    def is_pin_locked(self) -> bool:
        if not self.pin_locked_until:
            return False
        return timezone.now() < self.pin_locked_until

    # ---------------- Limits by KYC tier ----------------

    @property
    def daily_transaction_limit(self) -> int:
        """Max total naira value of transactions per day, based on KYC."""
        limits = {
            KYCTier.TIER_0: 5_000,
            KYCTier.TIER_1: 50_000,
            KYCTier.TIER_2: 200_000,
            KYCTier.TIER_3: 5_000_000,
        }
        return limits.get(self.kyc_tier, 5_000)

    @property
    def max_wallet_balance(self) -> int:
        """Max naira the wallet is allowed to hold."""
        limits = {
            KYCTier.TIER_0: 10_000,
            KYCTier.TIER_1: 100_000,
            KYCTier.TIER_2: 500_000,
            KYCTier.TIER_3: 10_000_000,
        }
        return limits.get(self.kyc_tier, 10_000)

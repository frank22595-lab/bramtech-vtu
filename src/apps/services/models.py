"""
Service catalog models.

Structure:
- Service: high-level category (Airtime, Data, Cable TV, Electricity, etc.)
- ServiceVariation: specific SKU (e.g. "MTN 1GB SME 7-day", "DStv Compact",
                     "IKEDC ₦1000 prepaid")
- TieredPricing: one price row per (variation, user_tier). Determines what
                 a user in each tier pays. Includes cost_price for margin
                 calculations.

Pricing lookup: services.pricing.get_price(user, variation) -> Decimal
"""
from __future__ import annotations

import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class ServiceCategory(models.TextChoices):
    """Top-level categories for service organization + admin filtering."""
    AIRTIME = "airtime", "Airtime"
    DATA = "data", "Data"
    CABLE_TV = "cable_tv", "Cable TV"
    ELECTRICITY = "electricity", "Electricity"
    EDUCATION = "education", "Education Pins"
    BETTING = "betting", "Betting"
    BROADBAND = "broadband", "Broadband"
    BULK_SMS = "bulk_sms", "Bulk SMS"


class Network(models.TextChoices):
    """
    Telco/provider network. Used for airtime, data, and some bill categories.
    Extend as more providers are added.
    """
    MTN = "mtn", "MTN"
    GLO = "glo", "Glo"
    AIRTEL = "airtel", "Airtel"
    NINEMOBILE = "9mobile", "9mobile"
    # Cable
    DSTV = "dstv", "DStv"
    GOTV = "gotv", "GOtv"
    STARTIMES = "startimes", "StarTimes"
    SHOWMAX = "showmax", "Showmax"
    # Electricity DisCos (add all 12 later)
    IKEDC = "ikedc", "Ikeja Electric"
    EKEDC = "ekedc", "Eko Electric"
    IBEDC = "ibedc", "Ibadan Electric"
    AEDC = "aedc", "Abuja Electric"
    PHEDC = "phedc", "Port Harcourt Electric"
    KEDCO = "kedco", "Kano Electric"
    KAEDCO = "kaedco", "Kaduna Electric"
    JEDC = "jedc", "Jos Electric"
    EEDC = "eedc", "Enugu Electric"
    BEDC = "bedc", "Benin Electric"
    YEDC = "yedc", "Yola Electric"
    AEDC_A = "aedc-a", "Aba Electric"
    # Betting
    BET9JA = "bet9ja", "Bet9ja"
    ONEXBET = "1xbet", "1xBet"
    SPORTYBET = "sportybet", "SportyBet"
    BETKING = "betking", "BetKing"
    NAIRABET = "nairabet", "NairaBet"
    # Exam
    WAEC = "waec", "WAEC"
    NECO = "neco", "NECO"
    JAMB = "jamb", "JAMB"
    NABTEB = "nabteb", "NABTEB"
    # Broadband
    SMILE = "smile", "Smile"
    SPECTRANET = "spectranet", "Spectranet"


class Service(models.Model):
    """
    Top-level service. Users select one, then a variation.

    Example: "Buy Data" -> variations: MTN 500MB, MTN 1GB, Glo 2GB, etc.
    """
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    category = models.CharField(
        max_length=20,
        choices=ServiceCategory.choices,
        db_index=True,
    )
    network = models.CharField(
        max_length=20,
        choices=Network.choices,
        db_index=True,
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    # Display order in UI
    display_order = models.IntegerField(default=0)

    # Icon/logo (path to static asset, filled later)
    icon = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services_service"
        ordering = ["category", "display_order", "name"]
        indexes = [
            models.Index(fields=["category", "network", "is_active"]),
        ]
        unique_together = ("category", "network", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.category})"


class VariationType(models.TextChoices):
    """
    How a variation is priced/consumed.

    FIXED: variation has a hard price (e.g. DStv Compact = ₦15,700).
    VARIABLE_AMOUNT: user chooses the amount (e.g. buying airtime — user
                     enters any amount, they pay face value).
    """
    FIXED = "fixed", "Fixed Price"
    VARIABLE_AMOUNT = "variable_amount", "Variable Amount (user chooses)"


class ServiceVariation(models.Model):
    """
    A specific purchasable SKU under a Service.

    - "MTN 1GB SME 7-day" is a variation of "MTN Data" service.
    - "DStv Compact" is a variation of "DStv" service.
    - Airtime is often modeled as a single VARIABLE_AMOUNT variation per network.

    The variation_code is the identifier the aggregator uses (e.g. Pairgate
    might expect "mtn_1gb_sme" for that data plan). Providers use this to
    look up the right SKU when dispatching.
    """
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="variations",
    )

    name = models.CharField(max_length=200, help_text="e.g. 'MTN 1GB SME 7-day'")
    variation_type = models.CharField(
        max_length=20,
        choices=VariationType.choices,
        default=VariationType.FIXED,
    )

    # Code the aggregator uses to identify this variation
    variation_code = models.CharField(max_length=100, db_index=True)

    # Only used when variation_type=FIXED — the face value / retail price
    # For VARIABLE_AMOUNT, user chooses the amount at purchase time.
    face_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    # Validity in days (for data plans, cable subscriptions)
    validity_days = models.IntegerField(null=True, blank=True)

    # Optional data volume in MB (for data plans)
    data_mb = models.IntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services_variation"
        ordering = ["service", "display_order", "face_value"]
        indexes = [
            models.Index(fields=["service", "is_active"]),
            models.Index(fields=["variation_code"]),
        ]

    def __str__(self) -> str:
        return f"{self.service.name} - {self.name}"

    @property
    def is_variable(self) -> bool:
        return self.variation_type == VariationType.VARIABLE_AMOUNT


class TieredPricing(models.Model):
    """
    Price a specific user tier pays for a specific variation, PLUS our cost.

    Every FIXED variation should have 5 rows (one per user tier).
    VARIABLE_AMOUNT variations use `discount_percent` — e.g. Gold tier gets
    2% off face value for airtime purchases.

    Margin = sale_price - cost_price (must be > 0 to prevent losses).
    """
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    variation = models.ForeignKey(
        ServiceVariation,
        on_delete=models.CASCADE,
        related_name="pricing",
    )
    user_tier = models.CharField(
        max_length=20,
        # We reference the choices dynamically to avoid circular import
        # (values must match apps.accounts.models.UserTier)
        choices=[
            ("regular", "Regular User"),
            ("bronze", "Bronze Reseller"),
            ("silver", "Silver Reseller"),
            ("gold", "Gold Reseller"),
            ("platinum", "Platinum Reseller"),
        ],
    )

    # What we pay the aggregator (COGS)
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    # ---- FIXED variation pricing ----
    # What this user tier pays
    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    # ---- VARIABLE_AMOUNT variation pricing ----
    # Percentage off face value for this tier (airtime style)
    # e.g. 3.00 means 3% off. User pays amount * (1 - 0.03).
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0"),
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services_tiered_pricing"
        unique_together = ("variation", "user_tier")
        indexes = [
            models.Index(fields=["variation", "user_tier", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.variation.name} @ {self.user_tier}"

    def margin(self, sale_amount: Decimal | None = None) -> Decimal:
        """
        Compute margin for this pricing row.
        For FIXED: margin = sale_price - cost_price.
        For VARIABLE: pass sale_amount (face value); returns (face - cost) after discount.
        """
        if self.variation.is_variable:
            if sale_amount is None:
                raise ValueError("sale_amount required for variable pricing margin")
            actual_sale = sale_amount * (Decimal("1") - (self.discount_percent or Decimal("0")) / Decimal("100"))
            actual_cost = sale_amount * (self.cost_price / Decimal("100")) if self.cost_price < 100 else self.cost_price
            # cost_price for VARIABLE is stored as a percentage of face value
            actual_cost = sale_amount * (self.cost_price / Decimal("100"))
            return actual_sale - actual_cost

        if self.sale_price is None:
            return Decimal("0")
        return self.sale_price - self.cost_price

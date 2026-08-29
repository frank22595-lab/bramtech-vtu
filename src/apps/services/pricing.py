"""
Pricing lookup service.

Central entry point: `get_price_for_user(user, variation, amount)`.
Handles both FIXED and VARIABLE_AMOUNT variations, returns the
sale price and cost price the user should be charged.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.core.cache import cache

from .models import ServiceVariation, TieredPricing, VariationType


class PricingError(Exception):
    """Base class for pricing errors."""


class NoPricingForTierError(PricingError):
    """No pricing row exists for the requested user tier."""


class InvalidAmountError(PricingError):
    """Requested amount is invalid."""


@dataclass(frozen=True)
class PriceQuote:
    """
    The result of a pricing lookup.

    Fields:
        sale_price: what the user pays (Naira)
        cost_price: what we pay the aggregator
        margin: sale_price - cost_price (must be > 0 for profitable trade)
        pricing_row: the underlying TieredPricing used (for audit)
    """
    sale_price: Decimal
    cost_price: Decimal
    margin: Decimal
    pricing_row: TieredPricing


def _cache_key(variation_id: int, tier: str) -> str:
    return f"pricing:v{variation_id}:t{tier}"


def get_pricing_row(variation: ServiceVariation, user_tier: str) -> TieredPricing:
    """
    Fetch the active TieredPricing row for (variation, tier).
    Cached for 5 minutes to avoid hammering the DB during peak.
    """
    key = _cache_key(variation.pk, user_tier)
    cached = cache.get(key)
    if cached is not None:
        return cached

    try:
        row = TieredPricing.objects.select_related("variation").get(
            variation=variation,
            user_tier=user_tier,
            is_active=True,
        )
    except TieredPricing.DoesNotExist:
        # Fallback to regular tier if user tier is missing
        if user_tier != "regular":
            try:
                row = TieredPricing.objects.select_related("variation").get(
                    variation=variation,
                    user_tier="regular",
                    is_active=True,
                )
            except TieredPricing.DoesNotExist:
                raise NoPricingForTierError(
                    f"No pricing for variation {variation.pk}, tier {user_tier} or fallback"
                )
        else:
            raise NoPricingForTierError(
                f"No pricing for variation {variation.pk}, tier {user_tier}"
            )

    cache.set(key, row, timeout=300)
    return row


def get_price_for_user(
    user, variation: ServiceVariation, amount: Decimal | None = None,
) -> PriceQuote:
    """
    Public pricing entrypoint.

    Args:
        user: the User buying the service. Their `tier` is used.
        variation: the ServiceVariation being purchased.
        amount: only used for VARIABLE_AMOUNT variations
                (the face value the user wants to buy).

    Returns:
        PriceQuote with sale_price, cost_price, margin.
    """
    tier = getattr(user, "tier", "regular")
    row = get_pricing_row(variation, tier)

    if variation.variation_type == VariationType.FIXED:
        sale = row.sale_price or variation.face_value or Decimal("0")
        cost = row.cost_price
        return PriceQuote(
            sale_price=sale,
            cost_price=cost,
            margin=sale - cost,
            pricing_row=row,
        )

    # VARIABLE_AMOUNT (e.g. airtime)
    if amount is None or amount <= 0:
        raise InvalidAmountError("A positive amount is required for variable pricing")

    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))

    discount_pct = row.discount_percent or Decimal("0")
    # Sale price = face value discounted for reseller tier
    sale = (amount * (Decimal("100") - discount_pct) / Decimal("100")).quantize(Decimal("0.01"))

    # Cost is stored as a percentage of face value (aggregator gives us X% off)
    # If cost_price stored as absolute Naira (>= 100), treat as absolute
    if row.cost_price >= 100:
        cost = row.cost_price
    else:
        cost = (amount * row.cost_price / Decimal("100")).quantize(Decimal("0.01"))

    return PriceQuote(
        sale_price=sale,
        cost_price=cost,
        margin=sale - cost,
        pricing_row=row,
    )

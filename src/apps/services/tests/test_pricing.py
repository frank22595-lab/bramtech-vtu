"""Tests for the services catalog and pricing."""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.services.models import (
    Network, Service, ServiceCategory, ServiceVariation,
    TieredPricing, VariationType,
)
from apps.services.pricing import (
    InvalidAmountError, NoPricingForTierError,
    get_price_for_user,
)

User = get_user_model()


@pytest.fixture
def mtn_data(db):
    service = Service.objects.create(
        category=ServiceCategory.DATA,
        network=Network.MTN,
        name="MTN Data",
        slug="mtn-data",
    )
    variation = ServiceVariation.objects.create(
        service=service,
        name="MTN 1GB SME 7-day",
        variation_type=VariationType.FIXED,
        variation_code="mtn_1gb_sme_7d",
        face_value=Decimal("500"),
        validity_days=7,
        data_mb=1024,
    )
    # Cost from aggregator: ₦285
    # Prices by tier: regular ₦500, bronze ₦420, silver ₦395, gold ₦370, platinum ₦345
    for tier, price in [
        ("regular", Decimal("500")),
        ("bronze", Decimal("420")),
        ("silver", Decimal("395")),
        ("gold", Decimal("370")),
        ("platinum", Decimal("345")),
    ]:
        TieredPricing.objects.create(
            variation=variation,
            user_tier=tier,
            cost_price=Decimal("285"),
            sale_price=price,
        )
    return variation


@pytest.fixture
def mtn_airtime(db):
    service = Service.objects.create(
        category=ServiceCategory.AIRTIME,
        network=Network.MTN,
        name="MTN Airtime",
        slug="mtn-airtime",
    )
    variation = ServiceVariation.objects.create(
        service=service,
        name="MTN Airtime",
        variation_type=VariationType.VARIABLE_AMOUNT,
        variation_code="mtn_airtime",
    )
    # cost_price stored as percentage of face (aggregator gives us 3% off = we pay 97%)
    # discount_percent: what we discount off face for the user
    for tier, discount in [
        ("regular", Decimal("0")),
        ("bronze", Decimal("1")),
        ("silver", Decimal("1.5")),
        ("gold", Decimal("2")),
        ("platinum", Decimal("2.5")),
    ]:
        TieredPricing.objects.create(
            variation=variation,
            user_tier=tier,
            cost_price=Decimal("97"),  # we pay 97% of face
            discount_percent=discount,
        )
    return variation


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(phone_number="08011110001", password="p", tier="regular")


@pytest.fixture
def gold_user(db):
    return User.objects.create_user(phone_number="08011110002", password="p", tier="gold")


@pytest.mark.django_db
class TestFixedPricing:
    def test_regular_user_pays_face_value(self, regular_user, mtn_data):
        quote = get_price_for_user(regular_user, mtn_data)
        assert quote.sale_price == Decimal("500")
        assert quote.cost_price == Decimal("285")
        assert quote.margin == Decimal("215")

    def test_gold_user_gets_discounted_price(self, gold_user, mtn_data):
        quote = get_price_for_user(gold_user, mtn_data)
        assert quote.sale_price == Decimal("370")
        assert quote.cost_price == Decimal("285")
        assert quote.margin == Decimal("85")

    def test_fallback_to_regular_when_tier_missing(self, gold_user, mtn_data):
        # Remove Gold pricing, Gold user should fall back to Regular
        TieredPricing.objects.filter(variation=mtn_data, user_tier="gold").delete()
        quote = get_price_for_user(gold_user, mtn_data)
        assert quote.sale_price == Decimal("500")  # regular price


@pytest.mark.django_db
class TestVariablePricing:
    def test_regular_user_pays_face_value_airtime(self, regular_user, mtn_airtime):
        quote = get_price_for_user(regular_user, mtn_airtime, amount=Decimal("1000"))
        assert quote.sale_price == Decimal("1000.00")   # no discount
        assert quote.cost_price == Decimal("970.00")    # 97% of face
        assert quote.margin == Decimal("30.00")

    def test_gold_user_gets_percentage_discount(self, gold_user, mtn_airtime):
        quote = get_price_for_user(gold_user, mtn_airtime, amount=Decimal("1000"))
        assert quote.sale_price == Decimal("980.00")   # 2% off face
        assert quote.cost_price == Decimal("970.00")   # still 97% of face
        assert quote.margin == Decimal("10.00")

    def test_variable_requires_amount(self, regular_user, mtn_airtime):
        with pytest.raises(InvalidAmountError):
            get_price_for_user(regular_user, mtn_airtime)

    def test_variable_zero_amount_rejected(self, regular_user, mtn_airtime):
        with pytest.raises(InvalidAmountError):
            get_price_for_user(regular_user, mtn_airtime, amount=Decimal("0"))


@pytest.mark.django_db
class TestMarginSafety:
    """
    Critical: no tier should ever have negative or zero margin.
    A misconfigured price could drain the aggregator wallet.
    """

    def test_all_tiers_have_positive_margin(self, mtn_data):
        for pricing in mtn_data.pricing.all():
            assert pricing.sale_price > pricing.cost_price, (
                f"Tier {pricing.user_tier} would lose money: "
                f"sale={pricing.sale_price} < cost={pricing.cost_price}"
            )

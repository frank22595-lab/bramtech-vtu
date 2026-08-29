"""Tests for the custom User model."""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.accounts.models import KYCTier, UserTier, normalize_ng_phone

User = get_user_model()


@pytest.mark.django_db
class TestPhoneNormalization:
    """Verify Nigerian phone numbers normalize correctly."""

    def test_local_format_08_prefix(self):
        assert normalize_ng_phone("08012345678") == "+2348012345678"

    def test_with_country_code_no_plus(self):
        assert normalize_ng_phone("2348012345678") == "+2348012345678"

    def test_with_plus_country_code(self):
        assert normalize_ng_phone("+2348012345678") == "+2348012345678"

    def test_with_spaces_and_dashes(self):
        assert normalize_ng_phone("+234 801 234 5678") == "+2348012345678"
        assert normalize_ng_phone("0801-234-5678") == "+2348012345678"

    def test_invalid_length_raises(self):
        with pytest.raises(ValidationError):
            normalize_ng_phone("080123456")  # too short

    def test_invalid_prefix_raises(self):
        with pytest.raises(ValidationError):
            normalize_ng_phone("06012345678")  # 060 isn't a Nigerian mobile prefix

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            normalize_ng_phone("")


@pytest.mark.django_db
class TestUserCreation:
    def test_create_user_with_phone_only(self):
        user = User.objects.create_user(
            phone_number="08012345678",
            password="testpass123",
        )
        assert user.phone_number == "+2348012345678"
        assert user.email is None
        assert user.check_password("testpass123")
        assert user.tier == UserTier.REGULAR
        assert user.kyc_tier == KYCTier.TIER_0
        assert user.referral_code  # auto-generated

    def test_create_user_normalizes_phone(self):
        user = User.objects.create_user(
            phone_number="+234 801 234 5679",
            password="pass",
        )
        assert user.phone_number == "+2348012345679"

    def test_create_user_lowercases_email(self):
        user = User.objects.create_user(
            phone_number="08012345671",
            password="pass",
            email="TEST@Example.COM",
        )
        assert user.email == "test@example.com"

    def test_referral_code_is_unique(self):
        u1 = User.objects.create_user(phone_number="08012345672", password="p")
        u2 = User.objects.create_user(phone_number="08012345673", password="p")
        assert u1.referral_code != u2.referral_code

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            phone_number="08099999999",
            password="adminpass",
        )
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.kyc_tier == KYCTier.TIER_3

    def test_phone_uniqueness_enforced(self):
        User.objects.create_user(phone_number="08012345674", password="p")
        with pytest.raises(Exception):  # IntegrityError from DB
            User.objects.create_user(phone_number="08012345674", password="p")


@pytest.mark.django_db
class TestTransactionPin:
    def test_set_and_check_pin(self):
        user = User.objects.create_user(phone_number="08012345675", password="p")
        user.set_transaction_pin("1234")
        user.save()

        assert user.check_transaction_pin("1234") is True
        assert user.check_transaction_pin("9999") is False

    def test_pin_must_be_digits(self):
        user = User.objects.create_user(phone_number="08012345676", password="p")
        with pytest.raises(ValidationError):
            user.set_transaction_pin("abcd")

    def test_pin_locks_after_5_failures(self):
        user = User.objects.create_user(phone_number="08012345677", password="p")
        user.set_transaction_pin("1234")
        user.save()

        for _ in range(5):
            user.check_transaction_pin("0000")

        assert user.is_pin_locked() is True
        # Even correct PIN fails when locked
        assert user.check_transaction_pin("1234") is False


@pytest.mark.django_db
class TestKYCLimits:
    def test_tier_0_default_limits(self):
        user = User.objects.create_user(phone_number="08012345678", password="p")
        assert user.daily_transaction_limit == 5_000
        assert user.max_wallet_balance == 10_000

    def test_higher_tier_has_higher_limits(self):
        user = User.objects.create_user(phone_number="08012345679", password="p")
        user.kyc_tier = KYCTier.TIER_3
        user.save()
        assert user.daily_transaction_limit == 5_000_000
        assert user.max_wallet_balance == 10_000_000

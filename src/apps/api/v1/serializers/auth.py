"""Auth-related serializers."""
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=100)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=100)
    referral_code = serializers.CharField(required=False, allow_blank=True, max_length=12)

    def validate_phone_number(self, value):
        try:
            return User.normalize_phone(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate(self, attrs):
        if User.objects.filter(phone_number=attrs["phone_number"]).exists():
            raise serializers.ValidationError({"phone_number": "Phone number already registered"})
        email = attrs.get("email")
        if email and User.objects.filter(email=email.lower()).exists():
            raise serializers.ValidationError({"email": "Email already in use"})
        return attrs

    def create(self, validated_data):
        referral_code = validated_data.pop("referral_code", "")
        password = validated_data.pop("password")
        referrer = None
        if referral_code:
            referrer = User.objects.filter(referral_code=referral_code.upper()).first()

        user = User.objects.create_user(
            phone_number=validated_data["phone_number"],
            password=password,
            email=validated_data.get("email") or None,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            referred_by=referrer,
        )
        return user


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            phone = User.normalize_phone(attrs["phone_number"])
        except DjangoValidationError:
            raise serializers.ValidationError({"phone_number": "Invalid phone number"})

        user = authenticate(phone_number=phone, password=attrs["password"])
        if not user or not user.is_active:
            raise serializers.ValidationError({"detail": "Invalid credentials"})

        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    wallet_balance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "public_id", "phone_number", "email", "first_name", "last_name",
            "full_name", "tier", "kyc_tier", "referral_code",
            "phone_verified", "email_verified", "wallet_balance",
            "date_joined",
        )
        read_only_fields = fields

    def get_wallet_balance(self, obj):
        wallet = getattr(obj, "wallet", None)
        if wallet:
            return str(wallet.balance)
        return "0.00"


class SetTransactionPinSerializer(serializers.Serializer):
    pin = serializers.CharField(min_length=4, max_length=6)

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN must be digits only")
        return value

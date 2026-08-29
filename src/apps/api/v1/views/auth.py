"""Auth endpoints — register, login, refresh, profile."""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers.auth import (
    LoginSerializer, RegisterSerializer,
    SetTransactionPinSerializer, UserSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user. Auto-creates a wallet (via signal).

    Body: {phone_number, password, email?, first_name?, last_name?, referral_code?}
    Returns: {user, access, refresh}
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Login with phone + password.

    Body: {phone_number, password}
    Returns: {user, access, refresh}
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    return Response({
        "user": UserSerializer(data["user"]).data,
        "access": data["access"],
        "refresh": data["refresh"],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Return the currently authenticated user's profile."""
    return Response(UserSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_pin(request):
    """Set or update the user's transaction PIN."""
    serializer = SetTransactionPinSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = request.user
    user.set_transaction_pin(serializer.validated_data["pin"])
    user.save()
    return Response({"detail": "PIN updated"})

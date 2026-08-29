"""URLs for the v1 REST API."""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import auth as auth_views
from .views import core as core_views

app_name = "v1"

urlpatterns = [
    # Auth
    path("auth/register/", auth_views.register, name="register"),
    path("auth/login/", auth_views.login, name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("auth/me/", auth_views.me, name="me"),
    path("auth/set-pin/", auth_views.set_pin, name="set-pin"),

    # Wallet
    path("wallet/", core_views.my_wallet, name="wallet"),
    path("wallet/virtual-accounts/", core_views.my_virtual_accounts, name="virtual-accounts"),

    # Services catalog
    path("services/", core_views.list_services, name="services"),
    path("services/<slug:service_slug>/variations/", core_views.list_variations, name="variations"),

    # Purchase
    path("purchase/", core_views.purchase, name="purchase"),

    # History
    path("transactions/", core_views.my_transactions, name="transactions"),
    path("transactions/<str:reference>/", core_views.transaction_detail, name="transaction-detail"),
]

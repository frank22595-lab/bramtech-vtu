"""
End-to-end transaction tests using the MockProvider.
Proves the full pipeline works: initiate -> debit -> dispatch -> success/failure/refund.
"""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.aggregators.models import (
    Aggregator, AggregatorRoute, AggregatorSKU, AggregatorStatus,
)
from apps.ledger.models import Account, AccountType
from apps.services.models import (
    Network, Service, ServiceCategory, ServiceVariation,
    TieredPricing, VariationType,
)
from apps.transactions.models import Transaction, TransactionStatus
from apps.transactions.services import (
    DuplicateTransactionError, NoRouteError, TransactionService,
)
from apps.wallets.services import (
    InsufficientFundsError, WalletService,
)

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(phone_number="08033330001", password="p", tier="regular")


@pytest.fixture
def variation_with_pricing(db):
    svc = Service.objects.create(
        category=ServiceCategory.DATA, network=Network.MTN,
        name="MTN Data", slug="mtn-data",
    )
    variation = ServiceVariation.objects.create(
        service=svc, name="1GB",
        variation_type=VariationType.FIXED,
        variation_code="mtn_1gb", face_value=Decimal("500"),
    )
    for tier in ["regular", "bronze", "silver", "gold", "platinum"]:
        TieredPricing.objects.create(
            variation=variation, user_tier=tier,
            cost_price=Decimal("285"),
            sale_price=Decimal("500") if tier == "regular" else Decimal("420"),
        )
    return variation


@pytest.fixture
def mock_aggregator(db, variation_with_pricing):
    # Create the ledger float account first
    Account.objects.create(
        account_type=AccountType.AGGREGATOR_FLOAT,
        code="aggregator_float:mock",
        name="Mock aggregator float",
        currency="NGN",
    )
    agg = Aggregator.objects.create(
        code="mock", name="Mock Provider",
        base_url="http://mock.local",
        status=AggregatorStatus.ACTIVE,
        ledger_account_code="aggregator_float:mock",
    )
    AggregatorRoute.objects.create(
        aggregator=agg, variation=variation_with_pricing,
        priority=1, is_active=True,
    )
    AggregatorSKU.objects.create(
        aggregator=agg, variation=variation_with_pricing,
        aggregator_sku_code="mock_1gb", is_active=True,
    )
    return agg


@pytest.fixture
def funded_wallet(user):
    """User with ₦2000 in their wallet."""
    wallet = WalletService.create_wallet_for_user(user)
    settlement = Account.objects.create(
        account_type=AccountType.PENDING_SETTLEMENT,
        code="pending_settlement:test",
        name="Settlement",
    )
    WalletService.credit(
        wallet, amount=Decimal("2000"),
        source_account=settlement, reference="fund-tx-test",
    )
    return wallet


@pytest.mark.django_db
class TestInitiate:
    def test_successful_initiation_debits_wallet(
        self, user, variation_with_pricing, mock_aggregator, funded_wallet, settings,
    ):
        settings.MOCK_PROVIDER_MODE = "always_success"
        tx = TransactionService.initiate(
            user=user, variation=variation_with_pricing,
            recipient="08099998888",
            idempotency_key="idem-001",
        )
        assert tx.status == TransactionStatus.PROCESSING
        assert tx.debit_journal is not None
        assert tx.sale_price == Decimal("500")
        assert tx.cost_price == Decimal("285")
        assert tx.margin == Decimal("215")

        funded_wallet.refresh_from_db()
        assert funded_wallet.balance == Decimal("1500")  # 2000 - 500

    def test_insufficient_funds_marks_failed(
        self, user, variation_with_pricing, mock_aggregator,
    ):
        WalletService.create_wallet_for_user(user)  # empty wallet
        with pytest.raises(InsufficientFundsError):
            TransactionService.initiate(
                user=user, variation=variation_with_pricing,
                recipient="08099998888",
                idempotency_key="idem-002",
            )

    def test_no_route_raises(self, user, variation_with_pricing, funded_wallet):
        # No aggregator setup -> should raise
        with pytest.raises(NoRouteError):
            TransactionService.initiate(
                user=user, variation=variation_with_pricing,
                recipient="08099998888",
                idempotency_key="idem-003",
            )

    def test_idempotency_returns_existing(
        self, user, variation_with_pricing, mock_aggregator, funded_wallet,
    ):
        tx1 = TransactionService.initiate(
            user=user, variation=variation_with_pricing,
            recipient="08099998888", idempotency_key="idem-dup",
        )
        tx2 = TransactionService.initiate(
            user=user, variation=variation_with_pricing,
            recipient="08099998888", idempotency_key="idem-dup",
        )
        assert tx1.pk == tx2.pk
        # Wallet only debited once
        funded_wallet.refresh_from_db()
        assert funded_wallet.balance == Decimal("1500")


@pytest.mark.django_db
class TestDispatch:
    def test_dispatch_success_marks_transaction_success(
        self, user, variation_with_pricing, mock_aggregator, funded_wallet, settings,
    ):
        settings.MOCK_PROVIDER_MODE = "always_success"
        tx = TransactionService.initiate(
            user=user, variation=variation_with_pricing,
            recipient="08099998888", idempotency_key="idem-s1",
        )
        TransactionService.dispatch(tx)
        tx.refresh_from_db()
        assert tx.status == TransactionStatus.SUCCESS
        assert tx.aggregator_reference.startswith("MOCK-")
        assert tx.completed_at is not None

        # Wallet stays debited
        funded_wallet.refresh_from_db()
        assert funded_wallet.balance == Decimal("1500")

    def test_dispatch_failure_refunds_wallet(
        self, user, variation_with_pricing, mock_aggregator, funded_wallet, settings,
    ):
        settings.MOCK_PROVIDER_MODE = "always_failed"
        tx = TransactionService.initiate(
            user=user, variation=variation_with_pricing,
            recipient="08099998888", idempotency_key="idem-f1",
        )
        TransactionService.dispatch(tx)
        tx.refresh_from_db()
        assert tx.status == TransactionStatus.FAILED
        assert tx.refund_journal is not None

        # Wallet fully refunded
        funded_wallet.refresh_from_db()
        assert funded_wallet.balance == Decimal("2000")

    def test_dispatch_is_idempotent_on_repeated_success(
        self, user, variation_with_pricing, mock_aggregator, funded_wallet, settings,
    ):
        settings.MOCK_PROVIDER_MODE = "always_success"
        tx = TransactionService.initiate(
            user=user, variation=variation_with_pricing,
            recipient="08099998888", idempotency_key="idem-rep",
        )
        TransactionService.dispatch(tx)
        TransactionService.dispatch(tx)  # second call
        tx.refresh_from_db()
        assert tx.status == TransactionStatus.SUCCESS
        funded_wallet.refresh_from_db()
        assert funded_wallet.balance == Decimal("1500")  # NOT double-debited


@pytest.mark.django_db
class TestMarginRecorded:
    def test_margin_is_correct(
        self, user, variation_with_pricing, mock_aggregator, funded_wallet, settings,
    ):
        settings.MOCK_PROVIDER_MODE = "always_success"
        tx = TransactionService.initiate(
            user=user, variation=variation_with_pricing,
            recipient="08099998888", idempotency_key="idem-margin",
        )
        assert tx.margin == tx.sale_price - tx.cost_price
        assert tx.margin > 0

"""
Django management command to seed the service catalog.

Usage:  docker compose exec django python manage.py seed_catalog
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.aggregators.models import (
    Aggregator, AggregatorRoute, AggregatorSKU, AggregatorStatus,
)
from apps.ledger.models import Account, AccountType
from apps.services.models import (
    Network, Service, ServiceCategory, ServiceVariation,
    TieredPricing, VariationType,
)


class Command(BaseCommand):
    help = "Seed the service catalog with sample services, variations, pricing, and mock aggregator"

    def handle(self, *args, **options):
        self.stdout.write("Seeding catalog...")

        # Ledger accounts
        for code, acc_type, name in [
            ("aggregator_float:mock", AccountType.AGGREGATOR_FLOAT, "Mock aggregator float"),
            ("platform_revenue:main", AccountType.PLATFORM_REVENUE, "Platform revenue"),
            ("pending_settlement:monnify", AccountType.PENDING_SETTLEMENT, "Monnify settlement"),
        ]:
            Account.objects.get_or_create(
                code=code,
                defaults={"account_type": acc_type, "name": name, "currency": "NGN"},
            )

        mock_agg, _ = Aggregator.objects.update_or_create(
            code="mock",
            defaults={
                "name": "Mock Provider", "base_url": "http://mock.local",
                "status": AggregatorStatus.ACTIVE,
                "ledger_account_code": "aggregator_float:mock",
            },
        )

        # MTN Airtime (variable)
        airtime_svc, _ = Service.objects.update_or_create(
            slug="mtn-airtime",
            defaults={
                "category": ServiceCategory.AIRTIME, "network": Network.MTN,
                "name": "MTN Airtime", "display_order": 1,
            },
        )
        airtime_var, _ = ServiceVariation.objects.update_or_create(
            service=airtime_svc, variation_code="mtn_airtime",
            defaults={"name": "MTN Airtime", "variation_type": VariationType.VARIABLE_AMOUNT},
        )
        for tier, disc in [("regular", 0), ("bronze", 1), ("silver", 1.5),
                            ("gold", 2), ("platinum", 2.5)]:
            TieredPricing.objects.update_or_create(
                variation=airtime_var, user_tier=tier,
                defaults={"cost_price": Decimal("97"), "discount_percent": Decimal(str(disc))},
            )
        AggregatorRoute.objects.update_or_create(
            variation=airtime_var, aggregator=mock_agg,
            defaults={"priority": 1, "is_active": True},
        )
        AggregatorSKU.objects.update_or_create(
            aggregator=mock_agg, variation=airtime_var,
            defaults={"aggregator_sku_code": "mtn_airtime", "is_active": True},
        )

        # MTN Data
        data_svc, _ = Service.objects.update_or_create(
            slug="mtn-data",
            defaults={
                "category": ServiceCategory.DATA, "network": Network.MTN,
                "name": "MTN Data", "display_order": 2,
            },
        )
        data_plans = [
            ("MTN 500MB SME 7d", "mtn_500mb", 300, 512, 150,
             {"regular": 300, "bronze": 260, "silver": 240, "gold": 220, "platinum": 200}),
            ("MTN 1GB SME 7d", "mtn_1gb", 500, 1024, 285,
             {"regular": 500, "bronze": 420, "silver": 395, "gold": 370, "platinum": 345}),
            ("MTN 2GB SME 14d", "mtn_2gb", 1000, 2048, 550,
             {"regular": 1000, "bronze": 830, "silver": 780, "gold": 730, "platinum": 680}),
            ("MTN 5GB SME 30d", "mtn_5gb", 2500, 5120, 1400,
             {"regular": 2500, "bronze": 2100, "silver": 1950, "gold": 1820, "platinum": 1700}),
        ]
        for name, code, face, mb, cost, tiers in data_plans:
            v, _ = ServiceVariation.objects.update_or_create(
                service=data_svc, variation_code=code,
                defaults={
                    "name": name, "variation_type": VariationType.FIXED,
                    "face_value": Decimal(str(face)), "data_mb": mb,
                    "validity_days": 7 if "7d" in name else (14 if "14d" in name else 30),
                },
            )
            for tier, price in tiers.items():
                TieredPricing.objects.update_or_create(
                    variation=v, user_tier=tier,
                    defaults={
                        "cost_price": Decimal(str(cost)),
                        "sale_price": Decimal(str(price)),
                    },
                )
            AggregatorRoute.objects.update_or_create(
                variation=v, aggregator=mock_agg,
                defaults={"priority": 1, "is_active": True},
            )
            AggregatorSKU.objects.update_or_create(
                aggregator=mock_agg, variation=v,
                defaults={"aggregator_sku_code": code, "is_active": True},
            )

        # DStv
        dstv_svc, _ = Service.objects.update_or_create(
            slug="dstv",
            defaults={
                "category": ServiceCategory.CABLE_TV, "network": Network.DSTV,
                "name": "DStv", "display_order": 10,
            },
        )
        for name, code, face, cost in [
            ("DStv Padi", "dstv_padi", 4400, 4350),
            ("DStv Yanga", "dstv_yanga", 6000, 5940),
            ("DStv Compact", "dstv_compact", 15700, 15550),
        ]:
            v, _ = ServiceVariation.objects.update_or_create(
                service=dstv_svc, variation_code=code,
                defaults={
                    "name": name, "variation_type": VariationType.FIXED,
                    "face_value": Decimal(str(face)), "validity_days": 30,
                },
            )
            for tier, price in [
                ("regular", face), ("bronze", face - 20), ("silver", face - 30),
                ("gold", face - 50), ("platinum", face - 70),
            ]:
                TieredPricing.objects.update_or_create(
                    variation=v, user_tier=tier,
                    defaults={
                        "cost_price": Decimal(str(cost)),
                        "sale_price": Decimal(str(price)),
                    },
                )
            AggregatorRoute.objects.update_or_create(
                variation=v, aggregator=mock_agg,
                defaults={"priority": 1, "is_active": True},
            )
            AggregatorSKU.objects.update_or_create(
                aggregator=mock_agg, variation=v,
                defaults={"aggregator_sku_code": code, "is_active": True},
            )

        self.stdout.write(self.style.SUCCESS("Done!"))
        self.stdout.write(f"  Services: {Service.objects.count()}")
        self.stdout.write(f"  Variations: {ServiceVariation.objects.count()}")
        self.stdout.write(f"  Pricing rows: {TieredPricing.objects.count()}")
        self.stdout.write(f"  Aggregators: {Aggregator.objects.count()}")

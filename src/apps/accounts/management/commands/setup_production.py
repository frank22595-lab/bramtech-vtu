"""One-shot production setup — creates superuser + funds mock aggregator."""
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "One-shot production setup"

    def handle(self, *args, **options):
        User = get_user_model()

        phone = os.environ.get('ADMIN_PHONE', '+2348137925907')
        password = os.environ.get('ADMIN_PASSWORD', 'ChangeThis2026!')

        if not User.objects.filter(phone_number=phone).exists():
            User.objects.create_superuser(
                phone_number=phone, password=password,
                email='bright22595@gmail.com',
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser created: {phone}'))
        else:
            self.stdout.write(f'Superuser {phone} already exists')

        from apps.ledger.models import Account, AccountType, Journal, JournalType
        from apps.ledger.services import LedgerService, EntrySpec

        if Journal.objects.filter(reference='seed-prod-mock-float').exists():
            self.stdout.write('Mock float already seeded')
            return

        try:
            mock = Account.objects.get(code='aggregator_float:mock')
        except Account.DoesNotExist:
            self.stdout.write(self.style.WARNING('Run seed_catalog first'))
            return

        external, _ = Account.objects.get_or_create(
            code='external:seed',
            defaults={'account_type': AccountType.SUSPENSE, 'name': 'Seed'},
        )
        LedgerService.post_journal(
            journal_type=JournalType.ADJUSTMENT,
            reference='seed-prod-mock-float',
            entries=[
                EntrySpec(mock, Decimal('1000000')),
                EntrySpec(external, Decimal('-1000000')),
            ],
            description='Seed mock aggregator with 1M NGN',
        )
        self.stdout.write(self.style.SUCCESS(f'Mock funded: {mock.balance()}'))

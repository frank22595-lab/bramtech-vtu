"""
Signals for wallets app.
Auto-creates a wallet when a User is created.
"""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .services import WalletService


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs) -> None:
    """When a new user is created, provision their wallet."""
    if created:
        WalletService.create_wallet_for_user(instance)

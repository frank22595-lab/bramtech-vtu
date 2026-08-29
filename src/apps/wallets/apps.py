from django.apps import AppConfig


class WalletsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.wallets"
    label = "wallets"
    verbose_name = "Wallets"

    def ready(self) -> None:
        # Import signal handlers
        from . import signals  # noqa: F401

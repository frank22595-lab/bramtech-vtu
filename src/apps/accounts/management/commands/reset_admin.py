from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        phone = "+2348137925907"
        password = "BramAdmin2026"
        user, created = User.objects.update_or_create(
            phone_number=phone,
            defaults={
                "email": "bright22595@gmail.com",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            }
        )
        user.set_password(password)
        user.save()
        print(f"Admin reset: phone={phone}, password={password}")

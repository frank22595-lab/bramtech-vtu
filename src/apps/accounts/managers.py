"""
Custom user manager for BramTech VTU.
Users register with phone number; email is optional.
"""
from __future__ import annotations

from typing import Any

from django.contrib.auth.base_user import BaseUserManager
from django.db import transaction


class UserManager(BaseUserManager):
    """
    Custom manager where phone_number is the unique identifier
    for authentication instead of usernames.
    """

    use_in_migrations = True

    def _create_user(
        self,
        phone_number: str,
        password: str | None = None,
        email: str | None = None,
        **extra_fields: Any,
    ):
        if not phone_number:
            raise ValueError("Phone number is required")

        # Normalise inputs
        phone_number = self.model.normalize_phone(phone_number)
        if email:
            email = self.normalize_email(email)

        with transaction.atomic():
            user = self.model(
                phone_number=phone_number,
                email=email,
                **extra_fields,
            )
            user.set_password(password)
            user.save(using=self._db)
        return user

    def create_user(
        self,
        phone_number: str,
        password: str | None = None,
        email: str | None = None,
        **extra_fields: Any,
    ):
        """Create and save a regular user."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, email, **extra_fields)

    def create_superuser(
        self,
        phone_number: str,
        password: str | None = None,
        email: str | None = None,
        **extra_fields: Any,
    ):
        """Create and save a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("kyc_tier", 3)  # Superuser bypasses KYC

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, password, email, **extra_fields)

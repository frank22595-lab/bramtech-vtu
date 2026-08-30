"""
Production settings.
Strict security, no debug info leaked.
"""
from .base import *  # noqa: F401, F403

DEBUG = False

# Strict allowed hosts (set via env)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")  # noqa: F405

# ==========================================
# Security Headers
# ==========================================
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HSTS — enable after your custom domain is on HTTPS
SECURE_HSTS_SECONDS = 0  # disable for now, enable after custom domain
SECURE_SSL_REDIRECT = False  # Render handles this at their proxy

# ==========================================
# Sentry (optional — install sentry-sdk to enable)
# ==========================================
SENTRY_DSN = env("SENTRY_DSN", default="")  # noqa: F405
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.django import DjangoIntegration
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration(), CeleryIntegration()],
            traces_sample_rate=0.1,
            send_default_pii=False,
            environment="production",
        )
    except ImportError:
        pass

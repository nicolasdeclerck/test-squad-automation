import os

import sentry_sdk

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
if "blog.nickorp.com" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("blog.nickorp.com")

if not SECRET_KEY:  # noqa: F405
    raise ValueError("SECRET_KEY environment variable is required in production")

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

SITE_URL = os.environ.get("SITE_URL", "https://blog.nickorp.com")
FRONTEND_INDEX_HTML = os.environ.get(
    "FRONTEND_INDEX_HTML",
    "/app/frontend/index.html",
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [
    "https://blog.nickorp.com",
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

CORS_ALLOWED_ORIGINS = [
    "https://blog.nickorp.com",
]

SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment=os.environ.get("SENTRY_ENV", "production"),
    )

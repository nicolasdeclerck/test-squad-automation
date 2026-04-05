import os

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
if "blog.nickorp.com" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("blog.nickorp.com")

if not SECRET_KEY:  # noqa: F405
    raise ValueError("SECRET_KEY environment variable is required in production")

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

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

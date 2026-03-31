from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

if not SECRET_KEY:  # noqa: F405
    SECRET_KEY = "django-insecure-dev-only-key-do-not-use-in-production"

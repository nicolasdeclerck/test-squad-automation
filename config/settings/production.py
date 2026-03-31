import os

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

if not SECRET_KEY:  # noqa: F405
    raise ValueError("SECRET_KEY environment variable is required in production")

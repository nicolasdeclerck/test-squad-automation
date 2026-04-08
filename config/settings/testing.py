"""
Settings for the ephemeral Docker TNR environment.
Mirrors production (gunicorn, built frontend, nginx) but safe for localhost HTTP.
"""

from .production import *  # noqa: F401, F403

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "nginx", "django"]

# HTTP-safe: no HTTPS enforcement for localhost
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = None

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

"""Production settings.

All sensitive values MUST come from the environment. There are no insecure
fallbacks here on purpose: missing required env vars should fail loudly.
"""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

# SECRET_KEY and ALLOWED_HOSTS are required and read from the environment
# in base.py. Fail fast if SECRET_KEY is not set.
if not SECRET_KEY:  # noqa: F405
    raise RuntimeError("SECRET_KEY environment variable must be set in production.")

# ---------------------------------------------------------------------------
# Security hardening (enable behind HTTPS)
# ---------------------------------------------------------------------------
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 7)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

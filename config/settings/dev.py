"""Development settings."""

from .base import *  # noqa: F401,F403
from .base import env

# Sensible dev defaults so the project runs out of the box even without a
# fully populated .env file.
DEBUG = env("DEBUG", default=True)

if not SECRET_KEY:  # noqa: F405
    SECRET_KEY = "django-insecure-dev-only-change-me"  # noqa: F811

ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])  # noqa: F811

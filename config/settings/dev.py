"""Development settings."""

from django.core.management.utils import get_random_secret_key

from .base import *  # noqa: F401,F403
from .base import env

# Sensible dev defaults so the project runs out of the box even without a
# fully populated .env file.
DEBUG = env("DEBUG", default=True)

if not SECRET_KEY:  # noqa: F405
    # Clave EFÍMERA y aleatoria por proceso (no una constante en el código).
    # Al reiniciar el server cambia; para persistir sesiones en dev definí
    # SECRET_KEY en el .env.
    SECRET_KEY = get_random_secret_key()  # noqa: F811

ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])  # noqa: F811

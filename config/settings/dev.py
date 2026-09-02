"""Development settings."""

from django.core.management.utils import get_random_secret_key

from .base import *  # noqa: F401,F403
from .base import env

# Sensible dev defaults so the project runs out of the box even without a
# fully populated .env file.
DEBUG = env("DEBUG", default=True)

if not SECRET_KEY:  # noqa: F405
    # Sin SECRET_KEY en el entorno, se genera una clave aleatoria y se
    # PERSISTE en un archivo local (git-ignored). Así no hay una constante
    # insegura en el código y, a la vez, la clave sobrevive a los reinicios
    # del server (no cierra la sesión de nadie en cada reinicio de dev).
    # En producción SECRET_KEY es obligatoria (ver production.py).
    _key_file = BASE_DIR / ".secret_key"  # noqa: F405
    if _key_file.exists():
        SECRET_KEY = _key_file.read_text().strip()  # noqa: F811
    else:
        SECRET_KEY = get_random_secret_key()  # noqa: F811
        _key_file.write_text(SECRET_KEY)

ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])  # noqa: F811

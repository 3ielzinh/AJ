"""
Configuracoes de producao.
Banco de dados: PostgreSQL.
Todas as variaveis sensiveis devem estar no .env da maquina de producao.
"""
from decouple import config, Csv
from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# ---------------------------------------------------------------------------
# Banco de dados PostgreSQL
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        # Reutiliza conexoes abertas por ate 120s para evitar overhead
        "CONN_MAX_AGE": config("CONN_MAX_AGE", default=120, cast=int),
    }
}

# ---------------------------------------------------------------------------
# Seguranca HTTP
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)

# ---------------------------------------------------------------------------
# Arquivos estaticos comprimidos pelo WhiteNoise
# ---------------------------------------------------------------------------
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

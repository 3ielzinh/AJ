"""
Configuracoes para servir na rede local (uso interno, sem SSL).
Usar apenas com waitress via INICIAR SERVIDOR.bat.
"""
from .base import *  # noqa: F401, F403
from decouple import config, Csv

DEBUG = False

# Permite acesso pelo IP local da máquina e por hostname
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

# Sem HTTPS forçado (rede local sem certificado)
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# Sessão expira em 8 horas
SESSION_COOKIE_AGE = 28800
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Segurança básica mantida
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Estáticos comprimidos
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

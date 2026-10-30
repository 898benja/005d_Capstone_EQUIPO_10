"""Configuración del proyecto FIX&GO — Django settings.

BE-14: CORS restringido por ambiente, DEBUG/SECRET_KEY/ALLOWED_HOSTS controlados.
BE-16: logging configurado con contexto (sin datos sensibles).
"""

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ---------------------------------------------------------------------------
# Seguridad (BE-14)
# ---------------------------------------------------------------------------

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    raise ImproperlyConfigured('Configura DJANGO_SECRET_KEY en backend/.env')

DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() == 'true'

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if h.strip()
]

# ---------------------------------------------------------------------------
# Apps y middleware
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'rest_framework', 'rest_framework.authtoken',
    'accounts', 'core', 'catalog', 'services', 'billing', 'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('SQLITE_PATH', BASE_DIR / 'db.sqlite3'),
    }
}

# ---------------------------------------------------------------------------
# Autenticación y usuarios
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Django REST Framework (BE-03, BE-11, BE-12)
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'accounts.authentication.ExpiringTokenAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # BE-03: límites de intentos por scope
    'DEFAULT_THROTTLE_RATES': {
        'login': '10/min',
        'register': '20/min',
    },
    # BE-12: paginación estable
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # BE-11: manejador de excepciones personalizado para errores normalizados
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

# BE-03: duración del token en horas (por defecto 24h)
TOKEN_EXPIRY_HOURS = int(os.environ.get('TOKEN_EXPIRY_HOURS', '24'))

# ---------------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Archivos estáticos
# ---------------------------------------------------------------------------

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# CORS (BE-14)
# En desarrollo se permite todo; en producción se restringe.
# ---------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
    if origin.strip()
]
# Si no hay orígenes configurados y estamos en DEBUG, permitir todo para desarrollo
CORS_ALLOW_ALL_ORIGINS = DEBUG and not CORS_ALLOWED_ORIGINS

# Permitir credenciales (cookies, Authorization header) en CORS
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Logging (BE-16)
# Registrar errores con contexto sin datos sensibles.
# ---------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # Log de la aplicación
        'accounts': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'catalog': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'services': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        # Log de Django
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# No habilita cobros reales. Requiere opt-in explícito y DEBUG para la demostración.
PAYMENTS_DEMO_ENABLED = os.environ.get('PAYMENTS_DEMO_ENABLED', 'false').lower() == 'true'
# Tasa ilustrativa, no determina el tratamiento tributario del comercio.
DEMO_VAT_PERCENT = int(os.environ.get('DEMO_VAT_PERCENT', '19'))

# Sustituible sin recompilar la app. Respetar atribución y caché del proveedor.
MAP_TILE_URL = os.environ.get('MAP_TILE_URL', 'https://tile.openstreetmap.org/{z}/{x}/{y}.png')
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', BASE_DIR / 'media')
DATA_UPLOAD_MAX_MEMORY_SIZE = 3 * 1024 * 1024

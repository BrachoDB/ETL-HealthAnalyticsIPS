import os
from pathlib import Path
import environ
import dj_database_url
from datetime import timedelta

# Initialize environment variables (django-environ for .env parsing in local)
env = environ.Env(
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file in local development. On Render the variables come from the
# service environment, so this is a no-op when the file does not exist.
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


def env_bool(name, default=False):
    """Safely read a boolean from the environment."""
    return os.environ.get(name, str(default)).strip().lower() in ('true', '1', 'yes', 'on')


def env_list(name, default=None):
    """Safely read a comma-separated list from the environment."""
    raw = os.environ.get(name)
    if not raw:
        return list(default or [])
    return [item.strip() for item in raw.split(',') if item.strip()]


# Quick-start development settings - unsuitable for production
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-change-me-in-production-please-use-a-real-secret-key',
)
DEBUG = env_bool('DEBUG', default=False)
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Render injects the public hostname of the service at runtime.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',

    # Local apps
    'apps.authentication',
    'apps.etl',
    'apps.analytics',
    'apps.ml',
    'apps.dashboard',
    'apps.reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise serves static files in production (must come right after security).
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database (MySQL - works locally with .env and in production with DATABASE_URL).
# We keep MySQL in every environment; only the connection target changes.
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'mysql://root:@127.0.0.1:3307/healthanalyticsips_db',
)

DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    ),
}

# Preserve the strict SQL mode used by the ETL pipeline.
DATABASES['default'].setdefault('OPTIONS', {})
DATABASES['default']['OPTIONS']['init_command'] = (
    "SET sql_mode='STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,"
    "ERROR_FOR_DIVISION_BY_ZERO'"
)

# SSL support for managed providers such as Aiven (SSL: REQUIRED).
# Enable it in production via DB_SSL_REQUIRED=True. Optionally point DB_SSL_CA
# to the Aiven ca.pem to also verify the server certificate.
if env_bool('DB_SSL_REQUIRED', default=False):
    DATABASES['default']['OPTIONS']['ssl_mode'] = os.environ.get('DB_SSL_MODE', 'REQUIRED')
    DB_SSL_CA = os.environ.get('DB_SSL_CA')
    if DB_SSL_CA:
        DATABASES['default']['OPTIONS']['ssl'] = {'ca': DB_SSL_CA}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (joblib ML models, ETL uploads, etc.)
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Storage backends: WhiteNoise compresses and fingerprints static assets.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# Simple JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Spectacular Configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'HealthAnalytics IPS API',
    'DESCRIPTION': 'API for clinical data analytics and risk prediction',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = env_bool('CORS_ALLOW_ALL_ORIGINS', default=False)
CORS_ALLOWED_ORIGINS = env_list(
    'CORS_ALLOWED_ORIGINS',
    default=['http://localhost:8000', 'http://127.0.0.1:8000'],
)
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS', default=[])
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

# Security Configuration
OPEN_REGISTRATION = env_bool('OPEN_REGISTRATION', default=False)
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', default=not DEBUG)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', default=not DEBUG)
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', default=False)
# Honor the X-Forwarded-Proto header set by Render's proxy so HTTPS is detected.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

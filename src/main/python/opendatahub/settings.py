"""
Django settings for opendatahub project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import datetime
import sys

import os
import dj_database_url


# SECURITY WARNING: don't run with debug turned on in production!
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/
DEBUG = bool(os.environ.get('DJANGO_DEBUG', False))
TEMPLATE_DEBUG = DEBUG
PRODUCTION = os.getenv('DJANGO_CONFIG') == 'PRODUCTION'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
WEBAPP_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'webapp')
WEBAPP_DIR = os.path.join(WEBAPP_ROOT, 'dist' if PRODUCTION else 'app')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r)gg!i^!6=62c8p416@n^x0@nc3#h)dj3ge10l*977u@np6=--'


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'mail_admins'],
            'propagate': True,
            'level': 'INFO' if not DEBUG else 'DEBUG',
        },
        'django.db.backends': {
            # otherwise prints the base64 encoded files which is simply too much for the console to handle
            'level': 'WARN',
            'propagate': True,
        },
        'Fiona': {
            # default verbosity slows down everything way too much
            'level': 'WARN',
            'propagate': True,
        },
        'fastkml': {
            # emits warnings if the file does not contains a geometry
            'level': 'ERROR'
        }
    },
}

ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')]

# correct protocol (http vs. https) when behind reverse proxy like heroku
USE_X_FORWARDED_HOST = True

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'rest_framework',
    'hub',
    'django.contrib.staticfiles',
    'rest_framework_jwt',
    'authentication',
    'rest_framework.authtoken',
    'social.apps.django_app.default',
)

# Dev. only, not required
try:
    import django_extensions  # noqa

    INSTALLED_APPS += ('django_extensions',)
except:
    pass

MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'opendatahub.middleware.error.ExceptionMiddleware',
)

ROOT_URLCONF = 'opendatahub.urls'

WSGI_APPLICATION = 'opendatahub.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'django.contrib.auth.context_processors.auth'
)
# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    # Heroku compliance
    'default': dj_database_url.config(default='postgres://opendatahub:opendatahub@localhost:5432/opendatahub')
}
CACHES = {
    # very short-lived basically for inter-request purposes only
    'L1': {
        # django.core.cache.backends.locmem.LocMemCache
        'BACKEND': 'opendatahub.utils.cache.locmem.LocMemNoPickleCache',
        'LOCATION': 'L1',
        'OPTIONS': {
            'TIMEOUT': 60,
            'MAX_ENTRIES': 100,
        }
    },
    # intermediate-lived general purpose memory cache
    'default': {
        'BACKEND': 'opendatahub.utils.cache.locmem.LocMemNoPickleCache',
        'LOCATION': 'L2',
        'OPTIONS': {
            'TIMEOUT': 300,
            'MAX_ENTRIES': 100,
        }
    },
    # persistent cache
    'L3': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'hub_cache',
        'OPTIONS': {
            'TIMEOUT': None,
            'MAX_ENTRIES': sys.maxint,
        }
    },
}


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'de-ch'

TIME_ZONE = 'Europe/Zurich'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# ACCOUNT_ADAPTER = 'authentication.adapters.MessageFreeAdapter'
AUTH_USER_MODEL = 'authentication.UserProfile'

SITE_ID = 1
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=14)
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATICFILES_DIRS = (WEBAPP_DIR,)
if DEBUG:
    STATICFILES_DIRS += (WEBAPP_ROOT,)

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'staticfiles')
STATIC_URL = '/static/'

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    'social.backends.facebook.FacebookOAuth2',
    # 'social.backends.github.GithubOAuth2',
    'authentication.backends.OdhGithubOAuth2'
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_by_email',  # <--- enable this one
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'authentication.pipelines.save_profile_picture'
)

JWT_ALLOW_REFRESH = True
JWT_AUTH_HEADER_PREFIX = "Bearer"
SOCIAL_AUTH_GITHUB_EXTRA_DATA = [('login', 'login')]
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_HOST_PASSWORD')
if EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'mail.gandi.net'
    EMAIL_HOST_USER = 'noreply@opendatahub.ch'
    EMAIL_PORT = 465
    EMAIL_USE_SSL = True
    SERVER_EMAIL = 'noreply@opendatahub.ch'
    DEFAULT_FROM_EMAIL = 'noreply@opendatahub.ch'
    ADMINS = (('Developers', 'devs@opendatahub.ch'),)

if not PRODUCTION:
    SSLIFY_DISABLE = True

"""
Django settings for opendatahub project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import logging
import datetime

import os
import dj_database_url


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PRODUCTION = os.getenv('CONFIGURATION') == 'PRODUCTION'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r)gg!i^!6=62c8p416@n^x0@nc3#h)dj3ge10l*977u@np6=--'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
logging.getLogger('Fiona').setLevel(logging.WARN)  # default verbosity slows down everything way too much
logging.basicConfig(level=logging.DEBUG)

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

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
    'django.contrib.staticfiles',
    'rest_framework',
    'hub',
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
    'formats': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'formats_cache',
        'TIMEOUT': 3000,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    },
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'default_cache'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# ACCOUNT_ADAPTER = 'authentication.adapters.MessageFreeAdapter'
AUTH_USER_MODEL = 'authentication.UserProfile'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
SITE_ID = 1
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=14)
}
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
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

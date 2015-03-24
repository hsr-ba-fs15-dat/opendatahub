"""
Django settings for opendatahub project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PRODUCTION = os.getenv('CONFIGURATION') == 'PRODUCTION'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r)gg!i^!6=62c8p416@n^x0@nc3#h)dj3ge10l*977u@np6=--'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


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

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

ACCOUNT_ADAPTER = 'authentication.adapters.MessageFreeAdapter'

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
    'social.backends.github.GithubOAuth2',
    'social.backends.twitter.TwitterOAuth',
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
JWT_DECODE_HANDLER = 'authentication.jwt_decode_handler'
# JWT_AUTH_HEADER_PREFIX = "Bearer"
# SOCIAL_AUTH_FACEBOOK_KEY = '401520096685508'
SOCIAL_AUTH_FACEBOOK_KEY = '401522313351953'
SOCIAL_AUTH_GITHUB_SECRET = 'a1bffb37d5d6050dc2d32bb43d7a9608df1d0fba'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

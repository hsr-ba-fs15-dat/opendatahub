"""
WSGI config for opendatahub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opendatahub.settings')

from django.core.wsgi import get_wsgi_application
from opendatahub.settings import STATIC_ROOT, DEBUG

application = get_wsgi_application()

if not DEBUG:
    from whitenoise.django import DjangoWhiteNoise
    application = DjangoWhiteNoise(application)
    application.add_files(os.path.join(STATIC_ROOT, 'bower_components'), prefix='bower_components/')
    application.add_files(os.path.join(STATIC_ROOT, 'scripts'), prefix='scripts/')
    application.add_files(os.path.join(STATIC_ROOT, 'styles'), prefix='styles/')
    application.add_files(os.path.join(STATIC_ROOT, 'views'), prefix='views/')
    application.add_files(os.path.join(STATIC_ROOT, 'images'), prefix='images/')
    application.add_files(os.path.join(STATIC_ROOT, 'favicons'), prefix='favicons/')
    application.add_files(os.path.join(STATIC_ROOT, 'fonts'), prefix='fonts/')
    application.add_files(os.path.join(STATIC_ROOT, 'favicon.ico'))
    application.files['/'] = application.get_static_file(os.path.join(STATIC_ROOT, 'index.html'), '/')

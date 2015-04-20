import os
from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers

from hub.views.transformation import TransformationViewSet
from opendatahub.settings import PRODUCTION, STATIC_ROOT, BASE_DIR
from hub.views.document import DocumentViewSet
from hub.views.file_group import FileGroupViewSet
from hub.views.file import FileViewSet
from hub.views.format import FormatView
from opendatahub.views import ConfigView
from hub.views.odhql import AdHocOdhQLView


router = routers.DefaultRouter(trailing_slash=True)
router.register(r'document', DocumentViewSet)
router.register(r'fileGroup', FileGroupViewSet)
router.register(r'file', FileViewSet)
router.register(r'format', FormatView, 'format')
router.register(r'config', ConfigView, 'config')
router.register(r'transformation', TransformationViewSet)

urlpatterns = (
    url(r'api/v1/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'api/v1/auth/', include('authentication.urls')),
    url(r'api/v1/odhql', AdHocOdhQLView.as_view()),
)

WEBAPP_DIR = os.path.join(os.path.dirname(BASE_DIR), 'webapp')

if PRODUCTION:
    WEBAPP_DIR = os.path.join(WEBAPP_DIR, 'dist')

    urlpatterns += (
        url(r'^$', 'django.views.static.serve', {'path': 'index.html', 'document_root': WEBAPP_DIR}),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),
        url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': WEBAPP_DIR}),
    )
else:
    WEBAPP_DIR = os.path.join(WEBAPP_DIR, 'app')

    urlpatterns += (
        url(r'^$', 'django.views.static.serve', {'path': 'index.html', 'document_root': WEBAPP_DIR}),
        url(r'^bower_components/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': '../webapp/bower_components'}),
        url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': WEBAPP_DIR}),
    )

urlpatterns = patterns('', *urlpatterns)

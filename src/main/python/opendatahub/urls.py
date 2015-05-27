# -*- coding: utf-8 -*-

""" URL route configuration. """

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers

from hub.views.transformation import TransformationViewSet
from opendatahub.settings import DEBUG, WEBAPP_DIR
from hub.views.document import DocumentViewSet
from hub.views.file_group import FileGroupViewSet
from hub.views.file import FileViewSet
from hub.views.format import FormatView
from hub.views.packages import PackageViewSet
from hub.views.url import UrlViewSet
from opendatahub.views import ConfigView, AngularErrorHandler
from hub.views.odhql import ParseView, DocumentationView


router = routers.DefaultRouter(trailing_slash=True)
router.register(r'config', ConfigView, 'config')
router.register(r'document', DocumentViewSet)
router.register(r'file', FileViewSet)
router.register(r'fileGroup', FileGroupViewSet)
router.register(r'format', FormatView, 'format')
router.register(r'package', PackageViewSet)
router.register(r'transformation', TransformationViewSet)
router.register(r'url', UrlViewSet)

urlpatterns = (
    url(r'api/v1/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'api/v1/auth/', include('authentication.urls')),
    url(r'api/v1/odhql/doc/', DocumentationView.as_view()),
    url(r'api/v1/parse/', ParseView.as_view()),
    url(r'api/v1/error_handler/', AngularErrorHandler.as_view()),
)

if DEBUG:
    urlpatterns += (
        url(r'^$', 'django.views.static.serve', {'path': 'index.html', 'document_root': WEBAPP_DIR}),
        url(r'^bower_components/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': '../webapp/bower_components'}),
        url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': WEBAPP_DIR}),
    )

urlpatterns = patterns('', *urlpatterns)

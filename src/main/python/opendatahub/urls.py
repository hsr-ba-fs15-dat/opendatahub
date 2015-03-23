from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers

from opendatahub.settings import PRODUCTION, STATIC_ROOT
from hub.views.document import DocumentViewSet
from hub.views.file_group import FileGroupViewSet
from hub.views.file import FileViewSet
from hub.views.format import FormatView


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'documents', DocumentViewSet)
router.register(r'fileGroups', FileGroupViewSet)
router.register(r'files', FileViewSet)
router.register(r'format', FormatView, 'format')

urlpatterns = (
    url(r'api/v1/?', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'api/v1/auth/', include('authentication.urls')),
)

if PRODUCTION:
    urlpatterns += (
        url(r'^$', 'django.views.static.serve', {'path': 'index.html', 'document_root': '../webapp/dist'}),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),
        url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': '../webapp/dist'}),
    )
else:
    urlpatterns += (
        url(r'^$', 'django.views.static.serve', {'path': 'index.html', 'document_root': '../webapp/app'}),
        url(r'^bower_components/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': '../webapp/bower_components'}),
        url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': '../webapp/app'}),
    )

urlpatterns = patterns('', *urlpatterns)

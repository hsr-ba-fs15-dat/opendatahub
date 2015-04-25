from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers

from hub.views.transformation import TransformationViewSet
from opendatahub.settings import PRODUCTION, WEBAPP_DIR
from hub.views.document import DocumentViewSet
from hub.views.file_group import FileGroupViewSet
from hub.views.file import FileViewSet
from hub.views.format import FormatView
from hub.views.url import UrlViewSet
from opendatahub.views import ConfigView
from hub.views.odhql import AdHocOdhQLView


router = routers.DefaultRouter(trailing_slash=True)
router.register(r'document', DocumentViewSet)
router.register(r'fileGroup', FileGroupViewSet)
router.register(r'file', FileViewSet)
router.register(r'url', UrlViewSet)
router.register(r'format', FormatView, 'format')
router.register(r'config', ConfigView, 'config')
router.register(r'transformation', TransformationViewSet)

urlpatterns = (
    url(r'api/v1/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'api/v1/auth/', include('authentication.urls')),
    url(r'api/v1/odhql', AdHocOdhQLView.as_view()),
)

if not PRODUCTION:
    urlpatterns += (url(r'^$', 'django.views.static.serve', {'path': 'index.html', 'document_root': WEBAPP_DIR}),)

urlpatterns = patterns('', *urlpatterns)

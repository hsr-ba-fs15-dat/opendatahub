from django.conf.urls import patterns, include, url
from django.contrib import admin
from opendatahub.settings import PRODUCTION

from rest_framework import routers
from hub.views import DocumentViewSet, RecordViewSet


router = routers.DefaultRouter()
router.register(r'documents', DocumentViewSet)
router.register(r'records', RecordViewSet)

from hub import views


urlpatterns = (
    # Examples:
    # url(r'^$', 'opendatahub.views.hub', name='hub'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^test/', views.test),
    url(r'api/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
)


if PRODUCTION:
    urlpatterns += (
        url(r'^$', 'django.views.static.serve', {'path': 'index.html', 'document_root': '../webapp/dist'}),
        url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': '../webapp/dist'}),
    )
else:
    urlpatterns += (
        url(r'^$', 'django.views.static.serve', {'path': 'index.html', 'document_root': '../webapp/app'}),
        url(r'^bower_components/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '../webapp/bower_components'}),
        url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': '../webapp/app'}),
    )


urlpatterns = patterns('', *urlpatterns)

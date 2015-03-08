from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework import routers
from hub.views import PipelineViewSet, NodeViewSet


router = routers.DefaultRouter()
router.register(r'pipelines', PipelineViewSet)
router.register(r'nodes', NodeViewSet)

from hub import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'opendatahub.views.hub', name='hub'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^test/', views.test),
    url(r'^$', 'django.views.static.serve', {'path': 'index.html', 'document_root': '../webapp/app'}),
    url(r'api/(?P<path>.*)$', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^bower_components/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '../webapp/bower_components'}),
    url(r'^styles/main\.css$', 'django.views.static.serve', {'path': '.tmp/styles/main.css', 'document_root': '../webapp'}),
    url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': '../webapp/app'}),
)

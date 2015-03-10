from django.conf.urls import patterns, include, url
from django.contrib import admin
from authentication.views import AccountViewSet, LoginView, LogoutView
from opendatahub.settings import PRODUCTION

from rest_framework import routers
from hub.views import DocumentViewSet, RecordViewSet
from opendatahub.views import IndexView


router = routers.DefaultRouter()
router.register(r'documents', DocumentViewSet)
router.register(r'records', RecordViewSet)
router.register(r'accounts', AccountViewSet)

from hub import views


urlpatterns = (
    # Examples:
    # url(r'^$', 'opendatahub.views.hub', name='hub'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^test/', views.test),
    url(r'api/v1/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/auth/login/$', LoginView.as_view(), name='login'),
    url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),

)

if PRODUCTION:
    urlpatterns += (
        url(r'^$', 'django.views.static.serve', {'path': 'index.html', 'document_root': '../webapp/dist'}),
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

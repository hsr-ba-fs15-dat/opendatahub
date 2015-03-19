from rest_framework import routers
from django.conf.urls import patterns, include, url

from authentication.views import SocialView, CurrentUserView


router = routers.DefaultRouter()

urlpatterns = (
    url(r'', include(router.urls)),
    url(r'^user/$', CurrentUserView.as_view(), name='user'),
    url(r'^facebook/$', SocialView.as_view(), name='fb_login'),

)
urlpatterns = patterns('', *urlpatterns)

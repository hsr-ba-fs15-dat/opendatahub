# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import routers
from django.conf.urls import patterns, include, url

from authentication.views import SocialView, CurrentUserView, PublicKeysView

""" URL route configuration. """

router = routers.DefaultRouter()

urlpatterns = (
    url(r'', include(router.urls)),
    url(r'^user/$', CurrentUserView.as_view(), name='user'),
    url(r'^social/$', SocialView.as_view(), name='fb_login'),
    url(r'^social/tokens/$', PublicKeysView.as_view(), name='fb_login'),
)
urlpatterns = patterns('', *urlpatterns)

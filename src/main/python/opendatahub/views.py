# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from rest_framework.viewsets import ViewSet
from django.http.response import JsonResponse
from django.core.mail import mail_admins
from django.views.generic import View
from django.views.decorators.cache import cache_page

from authentication.config import FACEBOOK_PUBLIC, GITHUB_PUBLIC
from opendatahub.settings import TRANSFORMATION_PREFIX, PACKAGE_PREFIX


class ConfigView(ViewSet):
    def list(self, request):
        return JsonResponse({
            'FACEBOOK_PUBLIC': FACEBOOK_PUBLIC,
            'GITHUB_PUBLIC': GITHUB_PUBLIC,
            'TRANSFORMATION_PREFIX': TRANSFORMATION_PREFIX,
            'PACKAGE_PREFIX': PACKAGE_PREFIX,
        })

    @classmethod
    def as_view(cls, actions=None, **initkwargs):
        # cache forever as it's impossible for it to change at runtime anyway
        return cache_page(None)(super(ConfigView, cls).as_view(actions, **initkwargs))


class AngularErrorHandler(View):
    def post(self, request):
        data = json.loads(request.body)
        stacktrace = data.get('stacktrace', '')
        message = data.get('message', '')
        url = data.get('url', '')
        cause = data.get('cause', '')

        mail_admins('JavaScript error for user "{}"'.format(request.user),
                    '{}: {}\n{}\n\nCause: {}\n\n\nRequest repr():\n{}'
                    .format(url, message, stacktrace, cause, request),
                    fail_silently=True)

        return JsonResponse({})

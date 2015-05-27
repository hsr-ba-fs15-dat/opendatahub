# -*- coding: utf-8 -*-
""" General views not directly involved in data hub business. """
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
    """ View for configuration settings (API keys, configuration settings, etc.) """
    def list(self, request):
        """ Returns configuration settings.
        :type request: rest_framework.request.Request
        :return: Response with configuration settings as JSON.
        """
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
    """ Accepts error reports from the client. Those are then sent via mail to a configured admin mail address. """
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

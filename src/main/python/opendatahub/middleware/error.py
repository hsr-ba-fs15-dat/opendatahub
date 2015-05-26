# -*- coding: utf-8 -*-

""" Django middleware for better handling of errors/warnigns. """

from __future__ import unicode_literals

import logging
import json

from django.http.response import JsonResponse, HttpResponseServerError, Http404
import warnings

from hub.exceptions import OdhWarning

logger = logging.getLogger(__name__)


class ExceptionMiddleware(object):
    """ Wraps exception for better user experience in case of errors. """
    def process_exception(self, request, exception):
        """ Wraps exceptions for ajax requests. """
        if request.is_ajax() and not isinstance(exception, Http404):
            status_code = HttpResponseServerError.status_code
            logger.error(exception.message, exc_info=True, extra={'status_code': status_code, 'request': request})
            return JsonResponse({'error': True, 'success': False}, status=status_code)


class WarningMiddleware(object):
    """ Displays warnings to the user. """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.is_ajax():
            with warnings.catch_warnings(record=True) as all_warnings:
                warnings.simplefilter('always', OdhWarning)
                response = view_func(request, *view_args, **view_kwargs)
                ws = [w.message.message for w in all_warnings if isinstance(w.message, OdhWarning)]
                if isinstance(response, JsonResponse) and ws:
                    response.content = '{{"_warnings": {}, "_data": {}}}'.format(json.dumps(ws), response.content)
                return response

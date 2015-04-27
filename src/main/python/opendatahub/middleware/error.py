import logging

from django.http.response import JsonResponse, HttpResponseServerError, Http404


logger = logging.getLogger(__name__)


class ExceptionMiddleware(object):
    def process_exception(self, request, exception):
        if request.is_ajax() and not isinstance(exception, Http404):
            status_code = HttpResponseServerError.status_code
            logger.error(exception.message, exc_info=True, extra={'status_code': status_code, 'request': request})
            return JsonResponse({'error': True, 'success': False}, status=status_code)

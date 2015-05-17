# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import inspect
import logging

from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.http.response import JsonResponse, HttpResponseBadRequest, HttpResponse
from pyparsing import ParseException
import docutils
import docutils.core
from django.views.decorators.cache import cache_page

from hub.odhql import parser
from hub.odhql.parser import OdhQLParser
from hub.odhql.functions.core import OdhQLFunction


logger = logging.getLogger(__name__)


class ParseView(View):
    @csrf_exempt
    def post(self, request):
        try:
            body = json.loads(request.body, encoding=request.encoding)
            params = body['params']

            statement = params['query']
            logger.debug('Validating ODHQL query "%s"', statement)

            query = OdhQLParser().parse(statement)
            query = [q.data_sources[0] for q in query.queries] if \
                isinstance(query, parser.Union) else query.data_sources

            data_sources = {'tables': [{'name': table.name, 'alias': table.alias} for table in query]}
        except ParseException as e:
            return JsonResponse({'error': e.message,
                                 'type': 'parse',
                                 'line': e.line,
                                 'lineno': e.lineno,
                                 'col': e.col},
                                status=HttpResponseBadRequest.status_code
                                )
        except MultiValueDictKeyError:
            return JsonResponse({'error': 'Es wurde keine ODHQL Abfrage angegeben.',
                                 'type': 'execution',  # todo check in frontend
                                 },
                                status=HttpResponseBadRequest.status_code
                                )

        return JsonResponse(data_sources)


class DocumentationView(View):
    def get(self, request):
        doc = """
        OpenDataHub Query Language (ODHQL)
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        .. contents:: Inhalt
            :backlinks: top

        {}
        {}
        """
        doc = inspect.cleandoc(doc).format(OdhQLParser.gen_doc(), OdhQLFunction.gen_all_docs())
        html = docutils.core.publish_parts(doc, writer_name='html', settings_overrides={'syntax_highlight': 'short'})[
            'html_body']
        html = html.replace('href="#', '<a du-smooth-scroll href="#')
        return HttpResponse(html)

    @classmethod
    def as_view(cls, **initkwargs):
        # cache forever as it's impossible for it to change at runtime anyway
        return cache_page(None)(super(DocumentationView, cls).as_view(**initkwargs))

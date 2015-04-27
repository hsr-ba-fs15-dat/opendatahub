import logging
import json
import itertools

from django.utils.datastructures import MultiValueDictKeyError

from django.views.generic import View
from django.http.response import JsonResponse, HttpResponseBadRequest
from pyparsing import ParseException

from hub.models import FileGroupModel

from hub.odhql import parser
from hub.odhql.exceptions import OdhQLExecutionException
from hub.odhql.interpreter import OdhQLInterpreter
from hub.utils.pandasutils import DataFrameUtils


logger = logging.getLogger(__name__)


class ParseView(View):
    def get(self, request):
        try:
            statement = request.GET['query']
            logger.debug('Validating ODHQL query "%s"', statement)
            parser.OdhQLParser().parse(statement)
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
                                 'type': 'execution',  # todo what exactly are we executing here?
                                 },
                                status=HttpResponseBadRequest.status_code
                                )

        return JsonResponse({'success': True})


class AdHocOdhQLView(View):
    def get(self, request):
        try:
            statement = request.GET['query']
            limit = int(request.GET.get('count', 3))
            page = int(request.GET.get('page', 1))
            start = limit * (page - 1)

            ids = OdhQLInterpreter.parse_sources(statement)

            fgs = FileGroupModel.objects.filter(id__in=ids.values())
            sources = {df.name: df for df in itertools.chain(*[fg.to_file_group().to_df() for fg in fgs])}
            sources = {name: sources[name] for name in ids.keys()}

            df = OdhQLInterpreter(sources).execute(statement)

        except OdhQLExecutionException as e:
            return JsonResponse({'error': e.message,
                                 'type': 'execution'},
                                status=HttpResponseBadRequest.status_code
                                )
        except ParseException as e:
            return JsonResponse({'error': e.message,
                                 'type': 'parse',
                                 'line': e.line,
                                 'lineno': e.lineno,
                                 'col': e.col},
                                status=HttpResponseBadRequest.status_code
                                )

        data = DataFrameUtils.to_json_dict(df, start, limit)
        return JsonResponse(data, encoder=json.JSONEncoder)

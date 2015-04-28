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
from hub.odhql.parser import OdhQLParser
from hub.utils.pandasutils import DataFrameUtils


logger = logging.getLogger(__name__)


class ParseView(View):
    def get(self, request):
        try:
            statement = request.GET['query']
            logger.debug('Validating ODHQL query "%s"', statement)
            query = OdhQLParser().parse(statement)
            query = [q.data_sources[0] for q in query.queries] if \
                isinstance(query, parser.Union) else query.data_sources
            print type(query)
            print query
            data_sources = {'tables': [{'name': table.name, 'alias': table.alias} for table in query]}
            print data_sources
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

        return JsonResponse(data_sources)


class AdHocOdhQLView(View):
    def get(self, request):
        try:
            statement = request.GET['query']
            limit = int(request.GET.get('count', 3))
            page = int(request.GET.get('page', 1))
            start = limit * (page - 1)

            ids = OdhQLInterpreter.parse_sources(statement)

            fgs = FileGroupModel.objects.filter(id__in=ids.values())
            # iteration over ((fg_id, df), (fg_id, df), ...)

            pairs = list(itertools.chain(*[zip(itertools.cycle([fg.id]), fg.to_file_group().to_df()) for fg in fgs]))
            sources = {'ODH{}_{}'.format(id, df.name): df for id, df in pairs}
            # allows for lookup without name -> ODH5 (takes the first table)
            sources.update({'ODH{}'.format(id): df for id, df in reversed(pairs)})
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

        data = DataFrameUtils.to_json_dict(df, None, start, limit)
        return JsonResponse(data, encoder=json.JSONEncoder)

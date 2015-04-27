import traceback
import logging
import json

from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import View
from django.http.response import JsonResponse, HttpResponseServerError, HttpResponseBadRequest

from pyparsing import ParseException

from hub.models import FileGroupModel
from hub.odhql import parser
from hub.odhql.exceptions import OdhQLExecutionException

from hub.odhql.interpreter import OdhQLInterpreter
from hub.odhql.parser import TokenException
from hub.utils.pandasutils import DataFrameUtils


logger = logging.getLogger(__name__)


class ParseView(View):
    def get(self, request):
        try:
            statement = request.GET['query']
            print statement
            odh_parser = parser.OdhQLParser()
            odh_parser.parse(statement)

        except ParseException as e:
            logging.error(traceback.format_exc())
            return JsonResponse({'error': e.message,
                                 'type': 'parse',
                                 'line': e.line,
                                 'lineno': e.lineno,
                                 'col': e.col},
                                status=HttpResponseBadRequest.status_code
                                )
        except MultiValueDictKeyError:
            logging.error(traceback.format_exc())
            return JsonResponse({'error': 'Es muss ein Query angegeben werden!',
                                 'type': 'execution',
                                 },
                                status=HttpResponseBadRequest.status_code
                                )

        except Exception:
            logging.error(traceback.format_exc())
            return JsonResponse({'error': True}, status=HttpResponseServerError.status_code)

        return JsonResponse({'success': True})


class AdHocOdhQLView(View):
    def get(self, request):
        try:
            statement = request.GET['query']
            limit = int(request.GET.get('count', 3))
            page = int(request.GET.get('page', 1))
            start = limit * (page - 1)

            ids = OdhQLInterpreter.parse_sources(statement)
            by_id = dict(zip(ids.values(), ids.keys()))

            fgs = FileGroupModel.objects.filter(id__in=ids.values())
            sources = {by_id[fg.id]: fg.to_file_group().to_df()[0] for fg in fgs}

            df = OdhQLInterpreter(sources).execute(statement)

        except (OdhQLExecutionException, TokenException) as e:
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

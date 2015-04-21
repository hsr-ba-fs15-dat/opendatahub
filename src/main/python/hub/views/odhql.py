import json
import traceback
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic import View
from django.http.response import JsonResponse, HttpResponseServerError
from pyparsing import ParseException

from hub.models import FileGroupModel
from hub.odhql.exceptions import OdhQLExecutionException
from hub.odhql.interpreter import OdhQLInterpreter
from hub.odhql.parser import TokenException
from hub.utils.pandasutils import DataFrameUtils


class JsonResponseServerError(HttpResponseServerError):
    """
    An HTTP response class that consumes data to be serialized to JSON.

    :param data: Data to be dumped into json. By default only ``dict`` objects
      are allowed to be passed due to a security flaw before EcmaScript 5. See
      the ``safe`` parameter for more information.
    :param encoder: Should be an json encoder class. Defaults to
      ``django.core.serializers.json.DjangoJSONEncoder``.
    :param safe: Controls if only ``dict`` objects may be serialized. Defaults
      to ``True``.
    """

    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True, **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError('In order to allow non-dict objects to be '
                            'serialized set the safe parameter to False')
        kwargs.setdefault('content_type', 'application/json')
        data = json.dumps(data, cls=encoder)
        super(JsonResponseServerError, self).__init__(content=data, **kwargs)


class AdHocOdhQLView(View):

    def get(self, request):
        try:
            statement = request.GET['query']
            limit = int(request.GET.get('count', 3))
            page = int(request.GET.get('page', 1))
            start = limit * page - 1

            ids = OdhQLInterpreter.parse_sources(statement)
            by_id = dict(zip(ids.values(), ids.keys()))

            fgs = FileGroupModel.objects.filter(id__in=ids.values())
            sources = {by_id[fg.id]: fg.to_file_group().to_df()[0] for fg in fgs}

            df = OdhQLInterpreter(sources).execute(statement)
        except (OdhQLExecutionException, TokenException) as e:
            return JsonResponseServerError({'error': e.message, 'type': 'execution'})
        except ParseException as e:
            return JsonResponseServerError({'error': e.message, 'type': 'parse', 'line': e.line, 'lineno': e.lineno,
                                 'col': e.col})
        except Exception as e:
            logging.error(traceback.format_exc())
            return JsonResponse({'error': True})

        data = DataFrameUtils.to_json_dict(df, start, limit)
        return JsonResponse(data)

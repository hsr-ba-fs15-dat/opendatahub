from django.views.generic import View
from django.http.response import JsonResponse

from hub.models import FileGroupModel
from hub.odhql.interpreter import OdhQLInterpreter
from hub.utils.pandasutils import DataFrameUtils


class AdhocOdhqlView(View):
    def get(self, request):
        statement = request.GET['query']
        request.GET.get('rows', 10)  # todo

        ids = OdhQLInterpreter.parse_sources(statement)
        by_id = dict(zip(ids.values(), ids.keys()))

        fgs = FileGroupModel.objects.filter(id__in=ids.values())
        sources = {by_id[fg.id]: fg.to_file_group().to_df() for fg in fgs}

        df = DataFrameUtils.make_serializable(OdhQLInterpreter(sources).execute(statement)).fillna('NULL')

        return JsonResponse({
            'columns': df.columns.tolist(),
            'data': df.to_dict(orient='records')
        })

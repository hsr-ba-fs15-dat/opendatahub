from django.views.generic import View
from django.http.response import JsonResponse

from hub.models import FileGroupModel
from hub.odhql.interpreter import OdhQLInterpreter
from hub.utils.pandasutils import DataFrameUtils


class AdHocOdhQLView(View):

    def get(self, request):
        statement = request.GET['query']
        count = int(request.GET.get('count', 3))
        page = int(request.GET.get('page', 1))
        start = count * page - 1

        ids = OdhQLInterpreter.parse_sources(statement)
        by_id = dict(zip(ids.values(), ids.keys()))

        fgs = FileGroupModel.objects.filter(id__in=ids.values())
        sources = {by_id[fg.id]: fg.to_file_group().to_df()[0] for fg in fgs}

        df = OdhQLInterpreter(sources).execute(statement)
        data = DataFrameUtils.to_json_dict(df, start, count)

        return JsonResponse(data)

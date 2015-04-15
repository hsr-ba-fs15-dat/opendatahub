from django.views.generic import View
from django.http.response import JsonResponse

from hub.models import FileGroupModel
from hub.odhql.interpreter import OdhQLInterpreter
from hub.utils.pandasutils import DataFrameUtils


class AdHocOdhQLView(View):

    def get(self, request):
        statement = request.GET['query']
        count = request.GET.get('count', 20)  # todo pagination features of rest framework?

        ids = OdhQLInterpreter.parse_sources(statement)
        by_id = dict(zip(ids.values(), ids.keys()))

        fgs = FileGroupModel.objects.filter(id__in=ids.values())
        sources = {by_id[fg.id]: fg.to_file_group().to_df() for fg in fgs}

        df = OdhQLInterpreter(sources).execute(statement).head(count).fillna('NULL')
        df = DataFrameUtils.make_serializable(df)

        return JsonResponse({
            'columns': df.columns.tolist(),
            'data': df.to_dict(orient='records')
        })

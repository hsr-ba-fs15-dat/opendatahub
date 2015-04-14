import zipfile
import types

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseServerError, JsonResponse

from hub.models import FileGroupModel, FileModel
from hub.serializers import FileGroupSerializer, FileSerializer
from authentication.permissions import IsOwnerOrPublic
from hub.utils.pandasutils import DataFrameUtils
import json
from hub.utils import cache


class FileGroupViewSet(viewsets.ModelViewSet):
    queryset = FileGroupModel.objects.all()
    serializer_class = FileGroupSerializer

    permission_classes = IsOwnerOrPublic,

    @detail_route()
    def file(self, request, pk, *args, **kwargs):
        queryset = FileModel.objects.filter(file_group__id=pk)
        serializer = FileSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route()
    def data(self, request, pk, *args, **kwargs):
        format_name = request.query_params.get('fmt', 'CSV')

        model = FileGroupModel.objects.get(id=pk)
        if not model:
            return HttpResponseNotFound(reason='No such file')

        group = model.to_file_group()

        response = HttpResponse()

        try:
            result_list = group.to_format(format_name)

            assert isinstance(result_list, types.ListType)

            if not result_list:
                return HttpResponseServerError(reason='Transformation failed: no result')

            if request.is_ajax():
                return JsonResponse({})  # just signal that it can be downloaded (200)

            if len(result_list) > 1 or len(result_list) > 0 and len(result_list[0].files) > 1:
                response['Content-Disposition'] = 'attachment; filename="odh-data.zip"'

                zip = zipfile.ZipFile(response, 'w')
                for result in result_list:
                    for file in result:
                        zip.writestr(file.name, file.stream.getvalue())
                zip.close()
            else:
                file = result_list[0][0]
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(file.name)
                response.write(file.stream.getvalue())

            response['Content-Type'] = 'application/octet-stream'
            response.flush()

            return response
        except:
            raise
            return HttpResponseServerError(reason='Transformation failed: no result')

    @detail_route()
    def preview(self, request, pk):
        try:
            model = FileGroupModel.objects.get(id=pk)
            cache_key = ('FG', pk, 'preview')
            data = cache.get(cache_key)
            cache.delete('FG', cascade=True)
            if not data:
                dataframes = model.to_file_group().to_df()
                
                data = []
                for df in dataframes:
                    preview = DataFrameUtils.make_serializable(df.head(3).fillna('NULL'))
                
                    data.append({
                        'columns': preview.columns.tolist(),
                        'data': preview.to_dict(orient='records'),
                    })
                cache.set(cache_key, data)

            return HttpResponse(content=json.dumps(data), content_type='application/json')
        except Exception as e:
            return JsonResponse({'error': e.message, 'error_location': 'preview'})

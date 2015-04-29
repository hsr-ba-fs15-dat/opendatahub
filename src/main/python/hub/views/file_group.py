import zipfile
import logging
import json

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseServerError, JsonResponse
from django.utils.text import slugify

from hub.models import FileGroupModel, FileModel
from hub.serializers import FileGroupSerializer, FileSerializer
from authentication.permissions import IsOwnerOrPublic
from hub.utils.pandasutils import DataFrameUtils
from opendatahub.utils.cache import cache


logger = logging.getLogger(__name__)


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
        result_list = cache.L1.get(('file_group', 'data', pk, format_name))

        model = FileGroupModel.objects.get(id=pk)
        if not model:
            return JsonResponse({'error': 'File does not exist'}, status=HttpResponseNotFound.status_code)

        if not result_list:
            group = model.to_file_group()

            result_list = group.to_format(format_name)

        if not result_list:
            return JsonResponse({'error': 'Conversion failed',
                                 'type': 'formatter'},
                                status=HttpResponseServerError.status_code)

        assert isinstance(result_list, (list, tuple))

        if request.is_ajax():
            cache.L1.set(('file_group', 'data', pk, format_name), result_list)
            return JsonResponse({})  # just signal that it can be downloaded (200)

        response = HttpResponse()
        if len(result_list) > 1 or len(result_list) > 0 and len(result_list[0].files) > 1:
            response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(
                slugify(unicode(model.document.name))[:200])

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

    @detail_route()
    def preview(self, request, pk):
        limit = int(request.GET.get('count', 3))
        page = int(request.GET.get('page', 1))
        start = limit * (page - 1)
        name = request.GET.get('name', None)

        model = FileGroupModel.objects.get(id=pk)
        dfs = model.to_file_group().to_df()

        if name:
            dfs = [df for df in dfs if df.name == name]

        data = [DataFrameUtils.to_json_dict(df, model.id, start, limit) for df in dfs]
        return JsonResponse(data, encoder=json.JSONEncoder, safe=False)

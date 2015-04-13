import zipfile

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseServerError, JsonResponse

from hub.models import FileGroupModel, FileModel
from hub.serializers import FileGroupSerializer, FileSerializer
from authentication.permissions import IsOwnerOrPublic
from hub.utils.pandasutils import DataFrameUtils


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
            result = group.to_format(format_name)

            if not result:
                return HttpResponseServerError(reason='Transformation failed: no result')

            if request.is_ajax():
                return JsonResponse({})  # just signal that it can be downloaded (200)

            if len(result.files) > 1:
                filename = group[0].basename + '.zip'
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

                zip = zipfile.ZipFile(response, 'w')
                for file in result:
                    zip.writestr(file.name, file.stream.getvalue())
                zip.close()
            else:
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(result[0].name)
                response.write(result[0].stream.getvalue())

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
            dataframes = model.to_file_group().to_df()

            return JsonResponse([{
                'columns': df.columns.tolist(),
                'data': df.iloc[:5].to_dict(orient='records')
            } for df in map(lambda df: DataFrameUtils.make_serializable(df).fillna('NULL'), dataframes)], safe=False)
        except Exception, e:
            raise
            # return JsonResponse({'error': e.message, 'error_location': 'preview'})

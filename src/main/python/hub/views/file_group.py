import zipfile

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseServerError

from hub.models import FileGroupModel, FileModel
from hub.serializers import FileGroupSerializer, FileSerializer


class FileGroupViewSet(viewsets.ModelViewSet):
    queryset = FileGroupModel.objects.all()
    serializer_class = FileGroupSerializer

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

            if len(result.files) > 1:
                response['Content-Disposition'] = 'attachment; filename="data.zip"'

                zip = zipfile.ZipFile(response, 'w')
                for file in result:
                    zip.writestr(file.name, file.stream.getvalue())
                zip.close()
            else:
                response['Content-Disposition'] = 'attachment; filename="%s"' % result[0].name
                response.write(result[0].stream.getvalue())
            response.flush()

            return response
        except:
            raise
            # return HttpResponseServerError()

    @detail_route()
    def preview(self, request, pk):
        return HttpResponseNotFound(reason='Testing!')

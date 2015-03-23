from rest_framework import viewsets
from rest_framework.decorators import detail_route
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseServerError

import zipfile

from hub.serializers import FileSerializer
from hub.models import FileModel


class FileViewSet(viewsets.ModelViewSet):
    queryset = FileModel.objects.all()
    serializer_class = FileSerializer

    @detail_route()
    def data(self, request, pk, *args, **kwargs):
        format_name = request.query_params.get('fmt', 'CSV')

        model = FileModel.objects.get(id=pk)

        if not model:
            return HttpResponseNotFound(reason='No such file')

        file = model.to_file()

        response = HttpResponse()

        try:
            result = file.to_format(format_name)
            if not result:
                return HttpResponseServerError(reason='Transformation failed: no result')

            if len(result.files) > 1:
                response['Content-Disposition'] = 'attachment; filename="data.zip"'

                zip = zipfile.ZipFile(response, 'w')
                for file in result.files:
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

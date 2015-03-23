from rest_framework import viewsets
from rest_framework.decorators import detail_route
from django.http.response import HttpResponse, HttpResponseNotFound

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
            return HttpResponseNotFound()

        file = model.to_file()

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="%s"' % file.name

        try:
            result = file.to_format(format_name)
            response.write(result)
            response.flush()

            return response
        except:
            raise
            # return HttpResponseServerError()


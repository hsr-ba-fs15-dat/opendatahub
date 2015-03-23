import urlparse

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse
import requests as http

from hub.serializers import DocumentSerializer, FileGroupSerializer
from hub.models import DocumentModel, FileGroupModel, FileModel
from hub.formatter import known_formatters
import hub.formatters
from hub.structures.file import File


print('Loaded formatters:')
print(hub.formatters.__all__)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = DocumentModel.objects.all()
    serializer_class = DocumentSerializer

    paginate_by = 50

    @detail_route()
    def data(self, request, pk, *args, **kwargs):
        format = request.query_params.get('fmt', 'plain')

        document = DocumentModel.objects.get(id=pk)
        files = FileModel.objects.filter(file_group__document=document)

        if len(files) == 0:
            return HttpResponse(status=404, reason='No such documents, or document not found')
        else:
            file = files[0]

            response = HttpResponse()
            response['Content-Disposition'] = 'attachment; filename="%s"' % file.name

        formatter_class = known_formatters.get(format)

        if not formatter_class:
            raise ValidationError('No such formatter')

        formatter = formatter_class()

        formatter.format(document, response, None)

        response.flush()

        return response

    def create(self, request, *args, **kwargs):
        """
        Create a document.
        Expected parameters: One of: url, file. Always: description
        """
        try:
            if not ('name' in request.data and 'description' in request.data):
                raise ValidationError('Insufficient information')

            doc = DocumentModel(name=request.data['name'], description=request.data['description'],
                                private=request.data.get('private', False))
            doc.save()

            file_group = FileGroupModel(document=doc, format=request.data.get('format', None))
            file_group.save()

            file = None

            if 'url' in request.data:
                url = request.data['url']

                resp = http.get(url)

                if resp.status_code != 200:
                    raise ValidationError('Failed to retrieve content: Status code %d' % resp.status_code)

                path = urlparse.urlparse(url)[2]

                if path:
                    filename = path.rsplit('/', 1)[1]
                else:
                    filename = (url[:250] + '...') if len(url) > 250 else url

                file = File(filename, resp.text.encode('utf8'))

                if not file:
                    raise ValidationError('Failed to read content')

                file_model = FileModel(file_name=file.name, data=file.stream, file_group=file_group)
                file_model.save()
            elif 'file' in request.data:
                files = request.data.getlist('file')
                for file in files:
                    file_model = FileModel(file_name=file.name, data=file.read(), file_group=file_group)
                    file_model.save()
            else:
                raise ValidationError('No data source specified')

            serializer = DocumentSerializer(DocumentModel.objects.get(id=doc.id), context={'request': request})

            return Response(serializer.data)
        except:
            raise  # ValidationError(detail='error handling input')

    def list(self, request, *args, **kwargs):
        """
        Search for documents. Valid query parameters:
        - name: Searches only in the name field.
        - description: Searches only in the description field.
        - search: searches all available text fields.
        Wildcards are not needed.
        """
        params = request.query_params

        documents = DocumentModel.objects.all()

        if 'name' in params:
            documents = documents.filter(name__icontains=params['name'])
        if 'description' in params:
            documents = documents.filter(description__icontains=params['description'])
        if 'search' in params:
            documents = documents.filter(Q(name__icontains=params['search']) |
                                         Q(description__icontains=params['search']))

        serializer = self.get_pagination_serializer(self.paginate_queryset(documents))
        return Response(serializer.data)

    @detail_route()
    def filegroups(self, request, pk, *args, **kwargs):
        queryset = FileGroupModel.objects.filter(document__id=pk)
        serializer = FileGroupSerializer(queryset, many=True, context={'request':request})
        return Response(serializer.data)
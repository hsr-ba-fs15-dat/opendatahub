from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse
import requests as http
import re

from hub.serializers import DocumentSerializer
from hub.models import DocumentModel, FileGroupModel, FileModel
from hub.formatter import known_formatters
import hub.formatters
from hub.parsers import Parser
from hub.formats import Format
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

        formatter_class = known_formatters.get(format)

        if not formatter_class:
            raise ValidationError('No such formatter')

        formatter = formatter_class()

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="data.%s"' % formatter.description.file_extension
        response['Content-Type'] = formatter.description.mime_type

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

            file_group = FileGroupModel(document=doc)
            file_group.save()

            file = None

            if 'url' in request.data:
                resp = http.get(request.data['url'])

                if resp.status_code != 200:
                    raise ValidationError('Failed to retrieve content: Status code %d' % resp.status_code)

                # extract last part of the path component
                match = re.search(r'/([^/]*)(?:\?#.*)$', request.data['url'])

                file = None
                if match:
                    filename = match.group(1)
                    file = File(filename, resp.text)
                elif 'format' in request.data:
                    format = filter(lambda n: n.label == request.data['format'], Format.formats)

                    if not format:
                        raise ValidationError('Unknown format')

                    file = File(request.data['url'], resp.text, format=format)

            elif 'file' in request.data:
                file = File(request.data['file'].name, request.data['file'])
            else:
                raise ValidationError('No data source specified')

            if not file:
                raise ValidationError('Failed to read content')

            file_model = FileModel(file_name=file.name, data=file.parse(), file_group=file_group)
            file_model.save()

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

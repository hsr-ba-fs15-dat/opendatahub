from rest_framework import viewsets

from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse
import requests as http

from hub.serializers import DocumentSerializer

from hub.models import DocumentModel
from hub.formatter import known_formatters
import hub.formatters

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
            content = ""

            if 'url' in request.data:
                resp = http.get(request.data['url'])

                if resp.status_code == 200:
                    content = resp.text
                else:
                    raise ValidationError('Failed to retrieve content: Status code %d' % resp.status_code)
            elif 'file' in request.data:
                content = request.data['file'].read()

            doc = DocumentModel(name=request.data['name'], description=request.data['description'], content=content)
            doc.save()

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

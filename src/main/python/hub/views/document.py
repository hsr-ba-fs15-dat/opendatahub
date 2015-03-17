import itertools

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse

from hub.serializers import DocumentSerializer, PaginatedRecordSerializer
from hub.models import DocumentModel, RecordModel
from hub.base import InputNode, ParserNode, FormatterNode
from hub.nodes import DatabaseWriter, DatabaseReader


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = DocumentModel.objects.all()
    serializer_class = DocumentSerializer

    paginate_by = 50

    @detail_route()
    def records(self, request, pk, *args, **kwargs):
        records = RecordModel.objects.filter(document__id=pk)
        records = self.paginate_queryset(records)
        serializer = PaginatedRecordSerializer(instance=records, context=self.get_serializer_context())
        return Response(serializer.data)

    @detail_route()
    def data(self, request, pk, *args, **kwargs):
        format = request.query_params.get('fmt', 'csv')  #kwargs.get('format', 'csv')

        reader = DatabaseReader()

        formatter = FormatterNode.find_node_for(format)
        if not formatter:
            raise ValidationError('no formatter')

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="data.%s"' % format

        read = reader.read({'document_id': pk})
        formatter.format(read, response)

        response.flush()

        return response

    def create(self, request, *args, **kwargs):
        """
        Create a document.
        Expected parameters: One of: url, file. Always: description
        """
        data = request.data

        input = None
        if 'url' in data:
            input = {'url': data['url']}
        if 'file' in data:
            input = {'file': data['file']}

        try:
            if input:
                node = InputNode.find_node_for(input)
                if node:
                    reader = node.read(input)

                    if reader:
                        peek = reader.next()
                        reader = itertools.chain([peek], reader)

                        node = ParserNode.find_node_for(peek)
                        if node:
                            reader = node.parse(reader)

                        writer = DatabaseWriter(name=data['name'], desc=data['description'])

                        doc = writer.write(reader)
                        serializer = DocumentSerializer(DocumentModel.objects.get(id=doc.id), context={'request': request})

                        return Response(serializer.data)
        except:
            pass

        raise ValidationError(detail='error handling input')

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

        serializer = self.get_pagination_serializer(
            self.paginate_queryset(documents))  # many=True, context={'request': request}
        return Response(serializer.data)

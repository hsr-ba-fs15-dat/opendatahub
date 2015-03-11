import itertools

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from hub.serializers import DocumentSerializer, RecordSerializer
from hub.models import DocumentModel, RecordModel
from hub.base import InputNode, ParserNode, FormatterNode
from hub.nodes import DatabaseWriter, DatabaseReader


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = DocumentModel.objects.all()
    serializer_class = DocumentSerializer

    @detail_route()
    def records(self, request, pk, *args, **kwargs):
        records = RecordModel.objects.filter(document__id=pk)
        serializer = RecordSerializer(records, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route()
    def data(self, request, pk, format='csv'):
        # format = request.query_params['format'] if 'format' in request.query_params else  'csv'

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
        '''
        Create a document.
        Expected parameters: One of: url, file. Always: description
        '''
        data = request.data

        input = None
        if 'url' in data:
            input = {'url': data['url']}
        if 'file' in data:
            input = {'file': data['file']}

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

        raise ValidationError(detail='error handling input')


class RecordViewSet(viewsets.ModelViewSet):
    queryset = RecordModel.objects.all()
    serializer_class = RecordSerializer


def test(request):
    return HttpResponse('test')

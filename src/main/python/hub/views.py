import itertools

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from hub.serializers import DocumentSerializer, RecordSerializer
from hub.models import DocumentModel, RecordModel
from hub.base import InputNode, TransformationNode
from hub.nodes import DatabaseWriter


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = DocumentModel.objects.all()
    serializer_class = DocumentSerializer

    @detail_route()
    def records(self, request, pk):
        records = RecordModel.objects.filter(document__id=pk)
        serializer = RecordSerializer(records, many=True, context={'request': request})
        return Response(serializer.data)

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

                peek = reader.next()
                reader = itertools.chain([peek], reader)

                node = TransformationNode.find_node_for(peek)
                if node:
                    reader = node.transform(reader)

                writer = DatabaseWriter(desc=data['description'])

                doc = writer.write(reader)
                serializer = DocumentSerializer(DocumentModel.objects.get(id=doc.id), context={'request': request})

                return Response(serializer.data)

        else:
            raise ValidationError(detail='unknown type')


class RecordViewSet(viewsets.ModelViewSet):
    queryset = RecordModel.objects.all()
    serializer_class = RecordSerializer


def test(r):
    return HttpResponse('test')

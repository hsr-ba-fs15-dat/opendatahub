from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from hub.serializers import DocumentSerializer, RecordSerializer
from hub.models import DocumentModel, RecordModel


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = DocumentModel.objects.all()
    serializer_class = DocumentSerializer

    @detail_route()
    def records(self, request, pk):
        records = RecordModel.objects.filter(document__id=pk)
        serializer = RecordSerializer(records, many=True, context={'request': request})
        return Response(serializer.data)


class RecordViewSet(viewsets.ModelViewSet):
    queryset = RecordModel.objects.all()
    serializer_class = RecordSerializer


def test(r):
    return HttpResponse('test')

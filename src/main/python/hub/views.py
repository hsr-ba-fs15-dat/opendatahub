from django.http import HttpResponse

from rest_framework import viewsets

from hub.serializers import PipelineSerializer, NodeSerializer
from hub.models import PipelineModel, NodeModel


# Create your views here.


class PipelineViewSet(viewsets.ModelViewSet):
    queryset = PipelineModel.objects.all()
    serializer_class = PipelineSerializer


class NodeViewSet(viewsets.ModelViewSet):
    queryset = NodeModel.objects.all()
    serializer_class = NodeSerializer


def test(r):
    return HttpResponse('test')
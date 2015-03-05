from hub.models import PipelineModel, NodeModel
from rest_framework import serializers


class PipelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineModel
        fields = ('name', 'description')


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeModel
        fields = ('pipeline', 'successor', 'params')

from rest_framework import serializers

from hub.models import DocumentModel, RecordModel


class RecordSerializer(serializers.HyperlinkedModelSerializer):
    content = serializers.ReadOnlyField()

    class Meta:
        model = RecordModel
        fields = ('id', 'url', 'document', 'content')


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DocumentModel
        fields = ('id', 'url', 'name', 'description')

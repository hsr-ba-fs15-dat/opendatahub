from rest_framework import serializers

from hub.models import DocumentModel, RecordModel


class RecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RecordModel
        fields = ('url', 'document', 'content')


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DocumentModel
        fields = ('url', 'description')

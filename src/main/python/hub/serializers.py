from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer

from hub.models import DocumentModel, RecordModel


class RecordSerializer(serializers.HyperlinkedModelSerializer):
    content = serializers.ReadOnlyField()

    class Meta:
        model = RecordModel
        fields = ('id', 'url', 'document', 'content')


class PaginatedRecordSerializer(PaginationSerializer):
    class Meta:
        object_serializer_class = RecordSerializer


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DocumentModel
        fields = ('id', 'url', 'name', 'description')


class PaginatedDocumentSerializer(PaginationSerializer):
    class Meta:
        object_serializer_class = DocumentSerializer

from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer

from hub.models import DocumentModel, FileGroupModel, FileModel


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    file_groups = serializers.HyperlinkedIdentityField('documentmodel-filegroups')

    class Meta:
        model = DocumentModel
        fields = ('id', 'url', 'name', 'description', 'file_groups')


class FileGroupSerializer(serializers.HyperlinkedModelSerializer):
    file_format = serializers.CharField(source='format')
    files = serializers.HyperlinkedIdentityField('filegroupmodel-files')

    class Meta:
        model = FileGroupModel
        fields = ('id', 'url', 'file_format', 'document', 'files')


class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FileModel
        fields = ('id', 'url', 'file_group')


class PaginatedDocumentSerializer(PaginationSerializer):
    class Meta:
        object_serializer_class = DocumentSerializer



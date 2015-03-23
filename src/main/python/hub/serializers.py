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
    data = serializers.HyperlinkedIdentityField('filemodel-data')
    class Meta:
        model = FileModel
        fields = ('id', 'url', 'file_name', 'file_group', 'data')


class PaginatedDocumentSerializer(PaginationSerializer):
    class Meta:
        object_serializer_class = DocumentSerializer


class FormatSerializer(serializers.Serializer):
    label = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    example = serializers.CharField(read_only=True)

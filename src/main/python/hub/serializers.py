from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer

from hub.models import DocumentModel, FileGroupModel, FileModel


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    file_groups = serializers.HyperlinkedIdentityField('documentmodel-filegroup')

    class Meta(object):
        model = DocumentModel
        fields = ('id', 'url', 'name', 'description', 'file_groups')


class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = FileModel
        fields = ('id', 'url', 'file_name', 'file_group')


class FileGroupSerializer(serializers.HyperlinkedModelSerializer):
    file_format = serializers.CharField(source='format')
    files = FileSerializer(many=True, read_only=True)

    document = DocumentSerializer(read_only=True)

    data = serializers.HyperlinkedIdentityField('filegroupmodel-data')

    preview = serializers.HyperlinkedIdentityField('filegroupmodel-preview')

    class Meta(object):
        model = FileGroupModel
        fields = ('id', 'url', 'file_format', 'document', 'files', 'data', 'preview')
        depth = 1


class PaginatedDocumentSerializer(PaginationSerializer):
    class Meta(object):
        object_serializer_class = DocumentSerializer


class FormatSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    example = serializers.CharField(read_only=True)

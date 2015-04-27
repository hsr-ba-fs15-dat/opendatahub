from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer

from authentication.serializers import UserSerializer
from hub.models import DocumentModel, FileGroupModel, FileModel, TransformationModel, UrlModel


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    file_groups = serializers.HyperlinkedIdentityField('documentmodel-filegroup')
    owner = UserSerializer(read_only=True)

    class Meta(object):
        model = DocumentModel
        fields = ('id', 'url', 'name', 'description', 'file_groups', 'private', 'owner', 'created_at')




class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = FileModel
        fields = ('id', 'url', 'file_name', 'file_group')


class UrlSerializer(serializers.HyperlinkedModelSerializer):
    source_url = serializers.URLField()

    class Meta(object):
        model = UrlModel
        fields = ('id', 'url', 'source_url', 'refresh_after', 'type', 'file_group')


class FileGroupSerializer(serializers.HyperlinkedModelSerializer):
    file_format = serializers.CharField(source='format')
    files = FileSerializer(many=True, read_only=True)
    urls = UrlSerializer(many=True, read_only=True)

    document = DocumentSerializer(read_only=True)

    data = serializers.HyperlinkedIdentityField('filegroupmodel-data')

    preview = serializers.HyperlinkedIdentityField('filegroupmodel-preview')

    class Meta(object):
        model = FileGroupModel
        fields = ('id', 'url', 'file_format', 'document', 'files', 'urls', 'data', 'preview')
        depth = 1


class PaginatedDocumentSerializer(PaginationSerializer):
    class Meta(object):
        object_serializer_class = DocumentSerializer


class FormatSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    example = serializers.CharField(read_only=True)


class TransformationSerializer(serializers.HyperlinkedModelSerializer):
    file_groups = FileGroupSerializer(many=True)
    owner = UserSerializer(read_only=True)

    class Meta(object):
        model = TransformationModel
        fields = ('id', 'url', 'name', 'description', 'transformation', 'private', 'owner', 'file_groups')

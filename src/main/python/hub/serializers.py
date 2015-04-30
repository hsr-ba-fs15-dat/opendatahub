from rest_framework import serializers

from authentication.serializers import UserSerializer
from hub.models import PackageModel, DocumentModel, FileGroupModel, FileModel, TransformationModel, UrlModel


class PackageSerializer(serializers.HyperlinkedModelSerializer):
    owner = UserSerializer(read_only=True)

    type = serializers.SerializerMethodField()

    class Meta(object):
        model = PackageModel
        fields = ('id', 'url', 'name', 'description', 'private', 'owner', 'created_at', 'type')

    def get_type(self, obj):
        if isinstance(obj, DocumentModel):
            return 'document'
        elif isinstance(obj, TransformationModel):
            return 'transformation'
        return 'unknown'


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    file_groups = serializers.HyperlinkedIdentityField('documentmodel-filegroup')
    owner = UserSerializer(read_only=True)

    class Meta(object):
        model = DocumentModel
        fields = ('id', 'url', 'name', 'description', 'file_groups', 'private', 'owner', 'created_at')

    def to_representation(self, instance):
        ret = super(DocumentSerializer, self).to_representation(instance)
        ret['type'] = 'document'
        return ret


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

    def to_representation(self, instance):
        ret = super(TransformationSerializer, self).to_representation(instance)
        ret['type'] = 'transformation'
        return ret

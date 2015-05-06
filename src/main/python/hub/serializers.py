# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.reverse import reverse

from authentication.serializers import UserDisplaySerializer
from hub.models import PackageModel, DocumentModel, FileGroupModel, FileModel, TransformationModel, UrlModel


class PackageSerializer(serializers.HyperlinkedModelSerializer):
    owner = UserDisplaySerializer(read_only=True)

    type = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()

    class Meta(object):
        model = PackageModel
        fields = ('id', 'url', 'name', 'description', 'private', 'owner', 'created_at', 'type', 'preview')

    def get_type(self, obj):
        if isinstance(obj, DocumentModel):
            return 'document'
        elif isinstance(obj, TransformationModel):
            return 'transformation'
        return 'unknown'

    def get_preview(self, obj):
        request = self.context.get('request', None)
        format = self.context.get('format', None)

        return reverse('{}model-preview'.format(self.get_type(obj)), kwargs={'pk': obj.id}, request=request,
                       format=format)


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    file_groups = serializers.HyperlinkedIdentityField('documentmodel-filegroup')
    owner = UserDisplaySerializer(read_only=True)

    class Meta(object):
        model = DocumentModel
        fields = ('id', 'url', 'name', 'description', 'file_groups', 'private', 'owner', 'created_at')

    def to_representation(self, instance):
        ret = super(DocumentSerializer, self).to_representation(instance)
        ret['type'] = 'document'
        return ret


class FileSerializer(serializers.HyperlinkedModelSerializer):
    file_format = serializers.CharField(source='format')

    class Meta(object):
        model = FileModel
        fields = ('id', 'url', 'file_name', 'file_format', 'file_group')


class UrlSerializer(serializers.HyperlinkedModelSerializer):
    source_url = serializers.URLField()
    url_format = serializers.CharField(source='format')

    class Meta(object):
        model = UrlModel
        fields = ('id', 'url', 'source_url', 'url_format', 'refresh_after', 'type', 'file_group')


class FileGroupSerializer(serializers.HyperlinkedModelSerializer):
    files = FileSerializer(many=True, read_only=True)
    urls = UrlSerializer(many=True, read_only=True)

    document = DocumentSerializer(read_only=True)

    data = serializers.HyperlinkedIdentityField('filegroupmodel-data')

    preview = serializers.HyperlinkedIdentityField('filegroupmodel-preview')

    class Meta(object):
        model = FileGroupModel
        fields = ('id', 'url', 'document', 'files', 'urls', 'data', 'preview')
        depth = 1


class FormatSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    example = serializers.CharField(read_only=True)


class TransformationSerializer(serializers.HyperlinkedModelSerializer):
    file_groups = FileGroupSerializer(many=True, read_only=True)
    owner = UserDisplaySerializer(read_only=True)

    preview = serializers.HyperlinkedIdentityField('transformationmodel-preview')

    class Meta(object):
        model = TransformationModel
        fields = ('id', 'url', 'name', 'description', 'transformation', 'private', 'owner', 'file_groups', 'preview')

    def to_representation(self, instance):
        ret = super(TransformationSerializer, self).to_representation(instance)
        ret['type'] = 'transformation'
        return ret

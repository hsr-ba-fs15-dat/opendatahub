# -*- coding: utf-8 -*-

# Get rid of "FormatSerializer:Method 'create' is abstract in class 'BaseSerializer' but is not overridden"
# FormatSerializer is read only anyway
# pylint: disable=abstract-method
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.reverse import reverse
from django.db.models import Q

from authentication.serializers import UserDisplaySerializer
from hub.models import PackageModel, DocumentModel, FileGroupModel, FileModel, TransformationModel, UrlModel

"""
Django serializers.
"""


class PackageSerializer(serializers.HyperlinkedModelSerializer):
    """
    Packages are either documents or transformations. Do some magic to differentiate between them (django/rest_framework
    is really bad at this).
    """
    owner = UserDisplaySerializer(read_only=True)

    type = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()
    template = serializers.SerializerMethodField()

    class Meta(object):
        """ Meta class for PackageSerializer. """
        model = PackageModel
        fields = ('id', 'url', 'name', 'description', 'private', 'owner', 'created_at', 'type', 'preview', 'template')

    def get_template(self, obj):
        if isinstance(obj, TransformationModel):
            return obj.is_template
        return False

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

    preview = serializers.HyperlinkedIdentityField('documentmodel-preview')

    class Meta(object):
        """ Meta class for DocumentSerializer. """
        model = DocumentModel
        fields = ('id', 'url', 'name', 'description', 'file_groups', 'private', 'owner', 'created_at', 'preview')

    def to_representation(self, instance):
        ret = super(DocumentSerializer, self).to_representation(instance)
        ret['type'] = 'document'
        return ret


class FileSerializer(serializers.HyperlinkedModelSerializer):
    file_format = serializers.CharField(source='format')

    class Meta(object):
        """ Meta class for FileSerializer. """
        model = FileModel
        fields = ('id', 'url', 'file_name', 'file_format', 'file_group')


class UrlSerializer(serializers.HyperlinkedModelSerializer):
    source_url = serializers.URLField()
    url_format = serializers.CharField(source='format')

    class Meta(object):
        """ Meta class for UrlSerializer. """
        model = UrlModel
        fields = ('id', 'url', 'source_url', 'url_format', 'refresh_after', 'type', 'file_group')


class TransformationIdSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='transformationmodel-detail')
    name = serializers.CharField(read_only=True)

    class Meta(object):
        fields = ('id', 'url', 'name')


class RelatedTransformationMixin(object):
    def _get_related_transformations(self, obj, request):
        filter = Q(private=False)
        if request.user:
            filter |= Q(owner=request.user.id)

        related_transformations = obj.related_transformations.filter(filter)

        serializer = TransformationIdSerializer(related_transformations, many=True, context={'request': request})
        return serializer.data


class FileGroupSerializer(serializers.HyperlinkedModelSerializer, RelatedTransformationMixin):
    files = FileSerializer(many=True, read_only=True)
    urls = UrlSerializer(many=True, read_only=True)

    document = DocumentSerializer(read_only=True)

    related_transformations = serializers.SerializerMethodField()

    data = serializers.HyperlinkedIdentityField('filegroupmodel-data')
    token = serializers.HyperlinkedIdentityField('filegroupmodel-token')
    preview = serializers.HyperlinkedIdentityField('filegroupmodel-preview')

    class Meta(object):
        """ Meta class for FileGroupSerializer. """
        model = FileGroupModel
        fields = ('id', 'url', 'document', 'files', 'urls', 'data', 'preview', 'related_transformations', 'token')
        depth = 1

    def get_related_transformations(self, obj):
        return self._get_related_transformations(obj, self.context['request'])


class FormatSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    example = serializers.CharField(read_only=True)
    extension = serializers.CharField(read_only=True)


class TransformationSerializer(serializers.HyperlinkedModelSerializer, RelatedTransformationMixin):
    referenced_file_groups = serializers.HyperlinkedIdentityField('transformationmodel-filegroups')
    referenced_transformations = serializers.HyperlinkedIdentityField('transformationmodel-transformations')
    token = serializers.HyperlinkedIdentityField('transformationmodel-token')

    related_transformations = serializers.SerializerMethodField()

    owner = UserDisplaySerializer(read_only=True)

    data = serializers.HyperlinkedIdentityField('transformationmodel-data')

    preview = serializers.HyperlinkedIdentityField('transformationmodel-preview')

    class Meta(object):
        """ Meta class for TransformationSerializer. """
        model = TransformationModel
        fields = ('id', 'url', 'name', 'description', 'transformation', 'private', 'owner', 'data', 'is_template',
                  'preview', 'referenced_file_groups', 'referenced_transformations', 'related_transformations', 'token')

    def to_representation(self, instance):
        ret = super(TransformationSerializer, self).to_representation(instance)
        ret['type'] = 'transformation'
        return ret

    def get_related_transformations(self, obj):
        return self._get_related_transformations(obj, self.context['request'])

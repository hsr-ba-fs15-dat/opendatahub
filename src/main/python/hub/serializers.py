from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer

from hub.models import DocumentModel


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    data = serializers.HyperlinkedIdentityField(view_name='documentmodel-data')

    class Meta:
        model = DocumentModel
        fields = ('id', 'url', 'data', 'name', 'description', 'data')


class PaginatedDocumentSerializer(PaginationSerializer):
    class Meta:
        object_serializer_class = DocumentSerializer

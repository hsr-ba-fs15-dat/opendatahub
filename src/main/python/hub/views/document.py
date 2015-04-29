from rest_framework import viewsets

from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction

from hub.serializers import DocumentSerializer, FileGroupSerializer

from hub.models import DocumentModel, FileGroupModel
from authentication.permissions import IsOwnerOrPublic, IsOwnerOrReadOnly
from hub.utils.upload import UploadHandler

from hub.views.mixins import FilterablePackageListViewSet


class DocumentViewSet(viewsets.ModelViewSet, FilterablePackageListViewSet):
    queryset = DocumentModel.objects.all()
    serializer_class = DocumentSerializer
    paginate_by_param = 'count'
    paginate_by = 20
    permission_classes = IsOwnerOrPublic, IsOwnerOrReadOnly,

    def create(self, request, *args, **kwargs):
        """
        Create a document.
        Expected parameters: One of: url, file. Always: description
        """
        if not ('name' in request.data and 'description' in request.data):
            raise ValidationError('Insufficient information')

        with transaction.atomic():
            doc = UploadHandler().handle_upload(request)

        serializer = DocumentSerializer(DocumentModel.objects.get(id=doc.id), context={'request': request})

        return Response(serializer.data)

    @detail_route()
    def filegroup(self, request, pk, *args, **kwargs):
        queryset = FileGroupModel.objects.filter(document__id=pk)
        serializer = FileGroupSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

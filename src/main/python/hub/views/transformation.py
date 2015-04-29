from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction

from hub.serializers import FileGroupSerializer, TransformationSerializer
from hub.models import FileGroupModel, TransformationModel
from authentication.permissions import IsOwnerOrPublic, IsOwnerOrReadOnly
from hub.views.mixins import FilterablePackageListViewSet


class TransformationViewSet(viewsets.ModelViewSet, FilterablePackageListViewSet):
    queryset = TransformationModel.objects.all()
    serializer_class = TransformationSerializer
    paginate_by_param = 'count'
    paginate_by = 20
    permission_classes = IsOwnerOrPublic, IsOwnerOrReadOnly,

    def create(self, request, *args, **kwargs):
        """
        Create a transformation.
        Expected parameters: One of: url, file. Always: description
        """
        if not ('name' in request.data and 'description' in request.data):
            raise ValidationError('Insufficient information')

        with transaction.atomic():
            doc = TransformationModel(name=request.data['name'], description=request.data['description'],
                                      private=request.data.get('private', False), owner=request.user,
                                      transformation=request.data.get('transformation'))
            doc.save()
            doc.file_groups.add(
                *[FileGroupModel.objects.get(id=str(fg)) for fg in request.data.get('file_groups')]
            )
            doc.save()

        serializer = TransformationSerializer(TransformationModel.objects.get(id=doc.id),
                                              context={'request': request})

        return Response(serializer.data)

    @detail_route()
    def filegroup(self, request, pk, *args, **kwargs):
        queryset = FileGroupModel.objects.filter(document__id=pk)
        serializer = FileGroupSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

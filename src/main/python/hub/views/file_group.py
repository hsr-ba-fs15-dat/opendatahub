from rest_framework import viewsets

from rest_framework.decorators import detail_route
from rest_framework.response import Response

from hub.models import FileGroupModel, FileModel
from hub.serializers import FileGroupSerializer, FileSerializer


class FileGroupViewSet(viewsets.ModelViewSet):
    queryset = FileGroupModel.objects.all()
    serializer_class = FileGroupSerializer

    @detail_route()
    def files(self, request, pk, *args, **kwargs):
        queryset = FileModel.objects.filter(file_group__id=pk)
        serializer = FileSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
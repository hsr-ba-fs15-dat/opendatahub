from rest_framework import viewsets

from hub.serializers import FileSerializer
from hub.models import FileModel


class FileViewSet(viewsets.ModelViewSet):
    queryset = FileModel.objects.all()
    serializer_class = FileSerializer

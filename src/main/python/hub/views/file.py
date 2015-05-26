# -*- coding: utf-8 -*-
""" Rest API for files. """

from __future__ import unicode_literals

from rest_framework import viewsets

from hub.serializers import FileSerializer
from hub.models import FileModel
from authentication.permissions import IsOwnerOrPublic


class FileViewSet(viewsets.ModelViewSet):
    """ ViewSet for files. """
    queryset = FileModel.objects.all()
    serializer_class = FileSerializer

    permission_classes = IsOwnerOrPublic,

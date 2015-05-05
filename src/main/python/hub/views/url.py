# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets

from hub.models import UrlModel
from hub.serializers import UrlSerializer
from authentication.permissions import IsOwnerOrPublic, IsOwnerOrReadOnly


class UrlViewSet(viewsets.ModelViewSet):
    queryset = UrlModel.objects.all()
    serializer_class = UrlSerializer
    paginate_by_param = 'count'
    paginate_by = 20
    permission_classes = IsOwnerOrPublic, IsOwnerOrReadOnly,

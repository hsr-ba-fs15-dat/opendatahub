# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.reverse import reverse

from hub.models import FileGroupModel, FileModel
from hub.serializers import FileGroupSerializer, FileSerializer
from authentication.permissions import IsOwnerOrPublic
from hub.views.mixins import DataDownloadMixin, PreviewMixin
from opendatahub import settings

logger = logging.getLogger(__name__)


class FileGroupViewSet(viewsets.ModelViewSet, DataDownloadMixin, PreviewMixin):
    queryset = FileGroupModel.objects.all()
    serializer_class = FileGroupSerializer

    permission_classes = IsOwnerOrPublic,

    cache_prefix = 'FG'

    @detail_route()
    def file(self, request, pk, *args, **kwargs):
        file = FileModel.objects.filter(file_group__id=pk)
        self.check_object_permissions(request, file)

        serializer = FileSerializer(file, many=True, context={'request': request})
        return Response(serializer.data)

    def format_object(self, model, format):
        group = model.to_file_group()

        if format:
            result_list = group.to_format(format)
        else:
            result_list = [group]
        return result_list

    def get_name(self, model):
        return model.document.name

    def get_preview_view_name(self, pk, request):
        reverse('filegroupmodel-preview', kwargs={'pk': pk}, request=request)

    def get_dfs_for_preview(self, pk, request):
        model = self.get_object()
        dfs = [('{}{}_{}'.format(settings.PACKAGE_PREFIX, pk, df.name), df) for df in model.to_file_group().to_df()]

        name = request.GET.get('name', None)
        if name:
            dfs = [(unique_name, df) for (unique_name, df) in dfs if unique_name == name]

        return dfs

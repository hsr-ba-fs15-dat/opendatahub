# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from urllib import unquote

import re
from rest_framework import viewsets
from rest_framework.response import Response

from rest_framework.decorators import detail_route, list_route

from rest_framework.reverse import reverse

from django.http.response import JsonResponse

from hub.models import FileGroupModel, FileModel
from hub.serializers import FileGroupSerializer, FileSerializer
from authentication.permissions import IsOwnerOrPublic
from hub.utils.odhql import TransformationUtil
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

    @list_route()
    def preview_by_unique_name(self, request):
        name = request.GET.get('name', None)
        if name:
            regex = r'^({0}|{1})(?P<id>\d+)_(?P<name>.*$)'.format(settings.PACKAGE_PREFIX,
                                                                  settings.TRANSFORMATION_PREFIX)
            match = re.search(regex, name)
            if match:
                pk = match.group('id')
                name = match.group('name')

                return self.preview(request, pk=pk, name=name)
        return JsonResponse({})

    def destroy(self, request, *args, **kwargs):
        TransformationUtil.invalidate_related_cache(file_groups={kwargs['pk']})
        return super(FileGroupViewSet, self).destroy(request, *args, **kwargs)

    def format_object(self, model, format):
        group = model.to_file_group()

        if format:
            result_list = group.to_format(format)
        else:
            result_list = [group]
        return result_list

    def get_name(self, model):
        return model.document.name

    def get_preview_view(self, pk, request):
        return reverse('filegroupmodel-preview', kwargs={'pk': pk}, request=request)

    def get_dfs_for_preview(self, pk, request):
        model = self.get_object()
        dfs = [('{}{}_{}'.format(settings.PACKAGE_PREFIX, pk, df.name), df)
               for df in model.to_file_group().to_df()]

        name = request.GET.get('name', None)
        if name:
            name = unquote(name)
            dfs = [(unique_name, df) for (unique_name, df) in dfs if unique_name == name]

        return dfs

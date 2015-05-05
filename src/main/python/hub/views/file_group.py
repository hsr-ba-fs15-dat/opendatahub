import logging
import json

import re
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.http.response import JsonResponse

from hub.models import FileGroupModel, FileModel
from hub.serializers import FileGroupSerializer, FileSerializer
from authentication.permissions import IsOwnerOrPublic
from hub.utils.pandasutils import DataFrameUtils
from opendatahub.settings import PACKAGE_PREFIX, TRANSFORMATION_PREFIX
from hub.views.mixins import DataDownloadMixin
from opendatahub import settings


logger = logging.getLogger(__name__)


class FileGroupViewSet(viewsets.ModelViewSet, DataDownloadMixin):
    queryset = FileGroupModel.objects.all()
    serializer_class = FileGroupSerializer

    permission_classes = IsOwnerOrPublic,

    cache_prefix = settings.TRANSFORMATION_PREFIX

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

    @list_route()
    def preview_by_unique_name(self, request):
        name = request.GET.get('name', None)
        if name:
            regex = r'^({0}|{1})(?P<id>\d+)_(?P<name>.*$)'.format(PACKAGE_PREFIX, TRANSFORMATION_PREFIX)
            m = re.search(regex, name)
            if m:
                fg_id = m.group('id')
                name = m.group('name')

                return self.preview(request, fg_id, name)
        return JsonResponse({})

    @detail_route()
    def preview(self, request, pk, name=None):
        limit = int(request.GET.get('count', 3))
        page = int(request.GET.get('page', 1))
        start = limit * (page - 1)
        name = name or request.GET.get('name', None)

        model = self.get_object()
        dfs = model.to_file_group().to_df()

        if name:
            dfs = [df for df in dfs if df.name == name]

        data = [DataFrameUtils.to_json_dict(df, model.id, start, limit) for df in dfs]
        return JsonResponse(data, encoder=json.JSONEncoder, safe=False)

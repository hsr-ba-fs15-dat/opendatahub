# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import zipfile
import json
import abc

import re
from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from django.http.response import HttpResponse, HttpResponseServerError, HttpResponseNotFound, JsonResponse
from django.utils.text import slugify

from opendatahub.utils.cache import cache
import logging

logger = logging.getLogger(__name__)


class FilterablePackageListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        """
        Search for documents. Valid query parameters:
        - name: Searches only in the name field.
        - description: Searches only in the description field.
        - search: searches all available text fields.
        Wildcards are not needed.
        """
        out = {'filter': {}, 'sorting': {}}
        params = dict(request.query_params.iterlists())
        parameter_regex = re.compile(r"^(filter|sorting)\[(\w+)\]$")
        for k, v in params.iteritems():
            m = re.match(parameter_regex, k)
            if m:
                out[m.group(1)][m.group(2)] = self.str2bool(v[0])

        if out:
            params.update(out)

        packages = self.get_queryset().filter(Q(owner=request.user.id) | Q(private=False))

        for key, filter in params['filter'].iteritems():
            if key == 'name':
                packages = packages.filter(name__icontains=filter)
            if key == 'description':
                packages = packages.filter(description__icontains=filter)
            if key == 'search':
                packages = packages.filter(Q(name__icontains=filter) |
                                           Q(description__icontains=filter))
            if key == 'mineOnly' and filter:
                packages = packages.filter(owner__id=request.user.id)

        packages = packages.order_by('id')
        for key, sort in params['sorting'].iteritems():
            packages = packages.order_by(key if sort == 'asc' else '-' + key)

        serializer = self.get_pagination_serializer(self.paginate_queryset(packages))
        return Response(serializer.data)

    def str2bool(self, v):
        if v.lower() in ('true', 'false'):
            return v.lower() == 'true'
        return v


class DataDownloadMixin(viewsets.GenericViewSet):
    cache_prefix = None

    @detail_route()
    def data(self, request, pk, *args, **kwargs):
        from hub.formats import Format

        format_name = request.query_params.get('fmt').lower() if 'fmt' in request.query_params else None

        cache_key = self.get_cache_key(pk, format_name)
        result_list = cache.L1.get(cache_key)

        model = self.get_object()

        if not model:
            return JsonResponse({'error': 'Object does not exist'}, status=HttpResponseNotFound.status_code)

        if not result_list:
            result_list = self.format_object(model, Format.from_string(format_name) if format_name else None)

        if not result_list:
            return JsonResponse({'error': 'Conversion failed', 'type': 'formatter'},
                                status=HttpResponseServerError.status_code)

        assert isinstance(result_list, (list, tuple))

        if request.is_ajax():
            cache.L1.set(cache_key, result_list)
            return JsonResponse({})  # just signal that it can be downloaded (200)

        response = HttpResponse()
        response['Content-Type'] = 'application/octet-stream'

        if len(result_list) > 1 or len(result_list) > 0 and len(result_list[0].files) > 1:
            response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(
                self.sanitize_name(self.get_name(model)))

            zip = zipfile.ZipFile(response, 'w')
            for result in result_list:
                for file in result:
                    zip.writestr(self.sanitize_name(file.name), file.stream.getvalue())
            zip.close()
        else:
            file = result_list[0][0]
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.sanitize_name(file.name))
            response.write(file.stream.getvalue())

        response.flush()

        return response

    def sanitize_name(self, name):
        sanitized = slugify(unicode(name))

        if not sanitized or len(sanitized.strip()) == 0:
            return 'odh'
        return sanitized[:200]

    def get_cache_key(self, pk, format_name=None):
        if format_name:
            return (self.cache_prefix, pk, 'data', format_name)
        return (self.cache_prefix, pk, 'data')

    def format_object(self, model, format):
        pass

    def get_name(self, model):
        pass


class PreviewMixin(viewsets.GenericViewSet):
    @detail_route()
    def preview(self, request, pk=None, name=None):
        count = int(request.GET.get('count', 3))
        page = int(request.GET.get('page', 1))
        start = count * (page - 1)

        data = []
        for (unique_name, df) in self.get_dfs_for_preview(pk, request):
            slice_ = df.iloc[start:start + count].reset_index(drop=True).as_safe_serializable().fillna('NULL')
            data.extend([{'name': getattr(df, 'name', None),
                          'unique_name': unique_name,
                          'columns': slice_.columns.tolist(),
                          'types': {c: s.odh_type.name for c, s in df.iteritems()},
                          'data': slice_.to_dict(orient='records'),
                          'count': len(df),
                          'parent': pk,
                          'url': self.get_preview_view_name(pk, request),
                          'type': 'preview'
                          }])
        return JsonResponse(data, encoder=json.JSONEncoder, safe=False)

    def get_preview_view_name(self, pk, request):
        pass

    @abc.abstractmethod
    def get_dfs_for_preview(self, pk, request):
        return []

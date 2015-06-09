# -*- coding: utf-8 -*-

""" Mixin classes for shared view functionality. """
from __future__ import unicode_literals
import ast
import calendar
import pickle

import zipfile
import json
import logging
import datetime

import abc
import re
from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http.response import HttpResponse, HttpResponseServerError, HttpResponseNotFound, JsonResponse, \
    HttpResponseForbidden
from django.utils.text import slugify
import os
from django.core import signing
from authentication.permissions import IsOwnerOrPublic
from hub.utils.common import str2bool
from opendatahub.utils.cache import cache


logger = logging.getLogger(__name__)


class FilterablePackageListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ Allows searching, pagination for package-based viewsets. """

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
                out[m.group(1)][m.group(2)] = str2bool(v[0])

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


class DataDownloadMixin(viewsets.GenericViewSet):
    """ Allows downloading of formattable data. """
    cache_prefix = None
    @detail_route(permission_classes=[IsOwnerOrPublic])
    def token(self, request, pk, *args, **kwargs):
        """

        :param request: rest_framework.request.Request
        :param pk: pk: unicode
        :param args: args: ignored
        :param kwargs: kwargs: ignored
        :return: Response with signed token
        """
        model = self.get_object()
        if not model:
            return JsonResponse({'error': 'Object does not exist'}, status=HttpResponseNotFound.status_code)
        valid = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        token = signing.dumps({'pk': pk, 'valid_until': calendar.timegm(valid.timetuple()),
                              'owner': pickle.dumps(request.user)})
        return JsonResponse({'token': token})

    @detail_route(permission_classes=[IsOwnerOrPublic])
    def data(self, request, pk, *args, **kwargs):
        """
        Download route.
        :type request: rest_framework.request.Request
        :type pk: unicode
        :param args: ignored
        :param kwargs: ignored
        :return: Response with formatted data.
        """
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
            token = ''
            return JsonResponse({'url': token})  # just signal that it can be downloaded (200)


        if True:
            response = HttpResponse()
            response['Content-Type'] = 'application/octet-stream'

            if len(result_list) > 1 or len(result_list) > 0 and len(result_list[0].files) > 1:
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(
                    self.sanitize_name(self.get_name(model) + '.zip'))

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
        """
        Gets rid of stuff in file names your filesystem probably doesn't handle too well (see
        http://www.eeemo.net/ and friends). Also, it's not like support for combining characters or chinese file names
        was a requirement.
        :type name: unicode
        :return: sanitized version of the file name.
        """
        parts = [slugify(unicode(s)) for s in os.path.splitext(name)]

        if not parts or len(parts[0].strip()) == 0:
            return 'odh'
        return '{}.{}'.format(parts[0][:196], parts[1])

    def get_cache_key(self, pk, format_name=None):
        """
        Generate a cache key for the requested data frames, so that requests in the near future don't take as long.
        :type pk: unicode
        :type format_name: unicode
        :return: Cache key.
        """
        if format_name:
            return (self.cache_prefix, pk, 'data', format_name)
        return (self.cache_prefix, pk, 'data')

    def format_object(self, model, format):
        """
        Format the object defined by the model in the given format.
        :param model: An instance of some model containing/pointing to data.
        :param format: Format the user asked for.
        :return: List of file groups with the formatted result.
        """
        pass

    def get_name(self, model):
        """
        Generate a file name for the given model.
        :param model: A model instance.
        :return: A sensible file name.
        """
        pass


class PreviewMixin(viewsets.GenericViewSet):
    """ Allows previewing of data. """

    @detail_route()
    def preview(self, request, pk=None, name=None):
        """
        Returns preview(s) for a given object.
        :type request: rest_framework.request.Request
        :type pk: object id
        :type name: name for the preview
        :return: Response containing the previews.
        """
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
                          'url': self.get_preview_view(pk, request),
                          'type': 'preview'}])
        return JsonResponse(data, encoder=json.JSONEncoder, safe=False)

    def get_preview_view(self, pk, request):
        """
        Get a view (url) for the specified object.
        :param pk: object id
        :param request: django request
        :return: url for the preview.
        """
        pass

    @abc.abstractmethod
    def get_dfs_for_preview(self, pk, request):
        """
        Get the data frames for the specified objects.
        :param pk: object id
        :param request: django request
        :return: data frames for the object.
        """
        return []

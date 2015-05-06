# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.http.response import JsonResponse
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseBadRequest
from django.utils.text import slugify
from pyparsing import ParseException
from rest_framework.reverse import reverse

from hub.odhql.interpreter import OdhQLInterpreter
from hub.odhql.exceptions import OdhQLExecutionException
from hub.serializers import FileGroupSerializer, TransformationSerializer
from hub.models import FileGroupModel, TransformationModel
from authentication.permissions import IsOwnerOrPublic, IsOwnerOrReadOnly
from hub.views.mixins import FilterablePackageListViewSet, DataDownloadMixin, PreviewMixin
from hub.utils.odhql import TransformationUtil
from hub import formatters
from hub.formats import CSV
from opendatahub.utils.cache import cache
from opendatahub import settings


class TransformationViewSet(viewsets.ModelViewSet, FilterablePackageListViewSet, DataDownloadMixin, PreviewMixin):
    queryset = TransformationModel.objects.all()
    serializer_class = TransformationSerializer
    paginate_by_param = 'count'
    paginate_by = 20
    permission_classes = IsOwnerOrPublic, IsOwnerOrReadOnly,

    cache_prefix = settings.TRANSFORMATION_PREFIX

    def create(self, request, *args, **kwargs):
        """
        Create a transformation.
        Expected parameters: One of: url, file. Always: description
        """
        if not ('name' in request.data and 'description' in request.data):
            raise ValidationError('Insufficient information')

        statement = request.data.get('transformation')

        file_group_ids = []
        transformation_ids = []
        is_template = False

        try:
            file_group_ids, transformation_ids = OdhQLInterpreter.parse_sources(statement)
        except OdhQLExecutionException:
            is_template = True

        with transaction.atomic():

            transformation = TransformationModel(name=request.data['name'], description=request.data['description'],
                                                 private=request.data.get('private', False), owner=request.user,
                                                 transformation=statement, is_template=is_template)
            transformation.save()

            if not is_template:
                transformation.referenced_file_groups.add(FileGroupModel.objects.filter(id_in=file_group_ids))
                transformation.referenced_transformations.add(
                    TransformationModel.objects.filter(id_in=transformation_ids))
                transformation.save()

        serializer = TransformationSerializer(TransformationModel.objects.get(id=transformation.id),
                                              context={'request': request})

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        id = self.get_object().id
        cache.delete((settings.TRANSFORMATION_PREFIX, id))

        return super(TransformationViewSet, self).update(request, *args, **kwargs)

    def format_object(self, model, format):
        try:
            df = TransformationUtil.df_for_transformation(model, user_id=self.request.user.id)
        except:
            return JsonResponse({'error': 'File does not exist'}, status=HttpResponseNotFound.status_code)

        if df is None:
            return JsonResponse({'error': 'Transformation returned no data'},
                                status=HttpResponseServerError.status_code)

        result_list = formatters.Formatter.format([df], slugify(unicode(model.name)),
                                                  format or CSV)

        return result_list

    def get_name(self, model):
        return model.name

    @detail_route()
    def filegroups(self, request, pk, *args, **kwargs):
        queryset = self.get_object().referenced_file_groups.all()
        serializer = FileGroupSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route()
    def transformations(self, request, pk, *args, **kwargs):
        queryset = self.get_object().referenced_transformations.all()
        serializer = TransformationSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def get_preview_view_name(self, pk, request):
        reverse('transformationmodel-{}'.format('preview' if pk else 'adhoc'), kwargs={'pk': pk}, request=request)

    def get_dfs_for_preview(self, pk, request):
        if pk is not None:
            return [('{}{}'.format(settings.TRANSFORMATION_PREFIX, pk),
                     TransformationUtil.df_for_transformation(self.get_object()))]
        else:
            body = json.loads(request.body, encoding=request.encoding)
            params = body['params']

            statement = params['query']
            return [(None, TransformationUtil.interpret(statement, user_id=request.user.id))]

    @list_route(methods={'post'})
    def adhoc(self, request):
        try:

            return self.preview(request)

        except OdhQLExecutionException as e:
            return JsonResponse({'error': e.message,
                                 'type': 'execution'},
                                status=HttpResponseBadRequest.status_code
                                )
        except ParseException as e:
            return JsonResponse({'error': e.message,
                                 'type': 'parse',
                                 'line': e.line,
                                 'lineno': e.lineno,
                                 'col': e.col},
                                status=HttpResponseBadRequest.status_code
                                )

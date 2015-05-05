# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.http.response import JsonResponse
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.utils.text import slugify

from hub.serializers import FileGroupSerializer, TransformationSerializer
from hub.models import FileGroupModel, TransformationModel
from authentication.permissions import IsOwnerOrPublic, IsOwnerOrReadOnly
from hub.views.mixins import FilterablePackageListViewSet, DataDownloadMixin
from hub.utils.odhql import TransformationUtil
from hub import formatters
from hub.formats import CSV
from opendatahub.utils.cache import cache
from opendatahub import settings


class TransformationViewSet(viewsets.ModelViewSet, FilterablePackageListViewSet, DataDownloadMixin):
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

        with transaction.atomic():
            doc = TransformationModel(name=request.data['name'], description=request.data['description'],
                                      private=request.data.get('private', False), owner=request.user,
                                      transformation=request.data.get('transformation'))
            doc.save()
            doc.file_groups.add(
                *[FileGroupModel.objects.get(id=str(fg)) for fg in request.data.get('file_groups')]
            )
            doc.save()

        serializer = TransformationSerializer(TransformationModel.objects.get(id=doc.id),
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
    def filegroup(self, request, pk, *args, **kwargs):
        queryset = FileGroupModel.objects.filter(document__id=pk)
        serializer = FileGroupSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

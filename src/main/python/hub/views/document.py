# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from django.http.response import HttpResponseNotFound, JsonResponse, HttpResponseBadRequest
from django.db import transaction
from django.db.models import Q

from hub.serializers import DocumentSerializer, FileGroupSerializer
from hub.models import DocumentModel, FileGroupModel
from authentication.permissions import IsOwnerOrPublic, IsOwnerOrReadOnly
from hub.utils.upload import UploadHandler
from hub.views.mixins import FilterablePackageListViewSet
from hub.parsers.base import NoParserException


class DocumentViewSet(viewsets.ModelViewSet, FilterablePackageListViewSet):
    queryset = DocumentModel.objects.all()
    serializer_class = DocumentSerializer
    paginate_by_param = 'count'
    paginate_by = 20
    permission_classes = IsOwnerOrPublic, IsOwnerOrReadOnly,

    def create(self, request, *args, **kwargs):
        """
        Create a document.
        Expected parameters: One of: url, file. Always: description
        """
        if not ('name' in request.data and 'description' in request.data):
            raise ValidationError('Insufficient information')

        try:
            with transaction.atomic():
                doc = UploadHandler().handle_upload(request)
        except NoParserException as e:
            return JsonResponse({'error': e.message,
                                 'type': e.__class__.__name__}, status=HttpResponseBadRequest.status_code)

        serializer = DocumentSerializer(DocumentModel.objects.get(id=doc.id), context={'request': request})

        return Response(serializer.data)

    @detail_route()
    def filegroup(self, request, pk, *args, **kwargs):
        file_group = FileGroupModel.objects.filter(
            Q(document__id=pk) & (Q(document__private=False) | Q(document__owner=request.user.id)))
        if not file_group:
            return HttpResponseNotFound()

        serializer = FileGroupSerializer(file_group, many=True, context={'request': request})
        return Response(serializer.data)

# -*- coding: utf-8 -*-

""" Rest API for documents. """

from __future__ import unicode_literals

from urllib import unquote

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.http.response import HttpResponseNotFound, JsonResponse, HttpResponseBadRequest
from django.db import transaction
from django.db.models import Q
from rest_framework.reverse import reverse

from opendatahub import settings
from hub.serializers import DocumentSerializer, FileGroupSerializer
from hub.models import DocumentModel, FileGroupModel
from authentication.permissions import IsOwnerOrPublic, IsOwnerOrReadOnly
from hub.utils.upload import UploadHandler
from hub.views.mixins import FilterablePackageListViewSet, PreviewMixin


class DocumentViewSet(viewsets.ModelViewSet, FilterablePackageListViewSet, PreviewMixin):
    """ ViewSet for documents. """
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
        from hub.formats import NoParserException

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
        """
        Lists the file groups of a document.

        :type request: rest_framework.request.Request
        :type pk: unicode
        :param args: ignored
        :param kwargs: ignored
        :return: response containing information about the filegroups for the selected document.
        """
        file_group = FileGroupModel.objects.filter(
            Q(document__id=pk) & (Q(document__private=False) | Q(document__owner=request.user.id)))
        if not file_group:
            return HttpResponseNotFound()

        serializer = FileGroupSerializer(file_group, many=True, context={'request': request})
        return Response(serializer.data)

    def get_preview_view(self, pk, request):
        """
        Gets the view for previews for this object.
        :param pk: id of the object.
        :param request: django request.
        :return: url for previews
        """
        return reverse('documentmodel-preview', kwargs={'pk': pk}, request=request)

    def get_dfs_for_preview(self, pk, request):
        """
        Gets the data frames for preview.
        :param pk: id of the object.
        :param request: django request
        :return: dataframes for the object.
        """
        file_groups = FileGroupModel.objects.filter(
            Q(document__id=pk) & (Q(document__private=False) | Q(document__owner=request.user.id)))

        dfs = []
        for fg in file_groups:
            for df in fg.to_file_group().to_df():
                dfs.append(('{}{}_{}'.format(settings.PACKAGE_PREFIX, fg.id, df.name), df))

        name = request.GET.get('name', None)
        if name:
            name = unquote(name)
            dfs = [(unique_name, df) for (unique_name, df) in dfs if unique_name == name]

        return dfs

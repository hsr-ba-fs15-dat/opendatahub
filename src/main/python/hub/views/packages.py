# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response

from hub.models import PackageModel, DocumentModel, InheritanceQuerySet
from hub.serializers import PackageSerializer, DocumentSerializer, TransformationSerializer
from hub.views.mixins import FilterablePackageListViewSet


class PackageViewSet(ReadOnlyModelViewSet, FilterablePackageListViewSet):
    queryset = InheritanceQuerySet(model=PackageModel).select_subclasses()
    serializer_class = PackageSerializer

    paginate_by_param = 'count'
    paginate_by = 20

    def retrieve(self, request, *args, **kwargs):
        pkg = self.get_object()
        serializer = DocumentSerializer if isinstance(pkg, DocumentModel) else TransformationSerializer

        return Response(serializer(pkg, context={'request': request}).data)

import collections

import re
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.db import transaction
import os

from hub.serializers import DocumentSerializer, FileGroupSerializer
from hub.models import DocumentModel, FileGroupModel

from hub.structures.file import File
from authentication.permissions import IsOwnerOrPublic, IsOwnerOrReadOnly

from hub.utils.upload import UploadHandler


class DocumentViewSet(viewsets.ModelViewSet):
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
                doc = UploadHandler().handleUpload(request)

            serializer = DocumentSerializer(DocumentModel.objects.get(id=doc.id), context={'request': request})

            return Response(serializer.data)
        except:
            raise  # ValidationError(detail='error handling input')


    def str2bool(self, v):
        if v.lower() in ('true', 'false'):
            return v.lower() in ('true', )
        return v

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
        prog = re.compile("^(filter|sorting)\[(\w+)\]$")
        for k, v in params.iteritems():
            m = re.match(prog, k)
            if m:
                out[m.group(1)][m.group(2)] = self.str2bool(v[0])
        if out:
            params.update(out)
        documents = DocumentModel.objects.all()

        for key, filt in params['filter'].iteritems():
            if key == 'name':
                documents = documents.filter(name__icontains=filt)
            if key == 'description':
                documents = documents.filter(description__icontains=filt)
            if key == 'search':
                documents = documents.filter(Q(name__icontains=filt) |
                                             Q(description__icontains=filt))
            if key == 'mineOnly' and filt:
                documents = documents.filter(owner__id=request.user.id)

        documents = documents.order_by('id')
        for key, sort in params['sorting'].iteritems():
            documents = documents.order_by('-' + key if sort == 'asc' else key)

        serializer = self.get_pagination_serializer(self.paginate_queryset(documents))
        return Response(serializer.data)

    @detail_route()
    def filegroup(self, request, pk, *args, **kwargs):
        queryset = FileGroupModel.objects.filter(document__id=pk)
        serializer = FileGroupSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

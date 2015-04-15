import urlparse
import collections

import re
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.db import transaction
import requests as http
import os

from hub.serializers import DocumentSerializer, FileGroupSerializer
from hub.models import DocumentModel, FileGroupModel, FileModel
import hub.formatters
from hub.structures.file import File
from authentication.permissions import IsOwnerOrPublic, IsOwnerOrReadOnly


print('Loaded formatters:')
print(hub.formatters.__all__)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = DocumentModel.objects.all()
    serializer_class = DocumentSerializer
    paginate_by_param = 'count'
    paginate_by = 50
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
                doc = DocumentModel(name=request.data['name'], description=request.data['description'],
                                    private=request.data.get('private', False), owner=request.user)
                doc.save()

                if 'url' in request.data:
                    self._handle_url(request, doc)
                elif 'file' in request.data:
                    self._handle_file(request, doc)
                else:
                    raise ValidationError('No data source specified')

            serializer = DocumentSerializer(DocumentModel.objects.get(id=doc.id), context={'request': request})

            return Response(serializer.data)
        except:
            raise  # ValidationError(detail='error handling input')

    def _handle_url(self, request, document):
        url = request.data['url']

        resp = http.get(url)

        if resp.status_code != 200:
            raise ValidationError('Failed to retrieve content: Status code %d' % resp.status_code)

        path = urlparse.urlparse(url)[2]

        if path:
            filename = path.rsplit('/', 1)[1]
        else:
            filename = (url[:250] + '...') if len(url) > 250 else url

        file = File(filename, resp.text.encode('utf8'))

        if not file:
            raise ValidationError('Failed to read content')

        file_group = FileGroupModel(document=document, format=request.data.get('format', None))
        file_group.save()

        file_model = FileModel(file_name=file.name, data=file.stream, file_group=file_group)
        file_model.save()

    def _handle_file(self, request, document):
        files = request.data.getlist('file')

        groups = collections.defaultdict(list)
        for file in files:
            name = os.path.splitext(file.name)[0]
            groups[name].append(file)

        for group in groups.itervalues():
            file_group = FileGroupModel(document=document, format=request.data.get('format', None))
            file_group.save()

            for file in group:
                file_model = FileModel(file_name=file.name, data=file.read(), file_group=file_group)
                file_model.save()

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
            documents = documents.order_by('-' + key if sort=='asc' else key)



        serializer = self.get_pagination_serializer(self.paginate_queryset(documents))
        return Response(serializer.data)

    @detail_route()
    def filegroup(self, request, pk, *args, **kwargs):
        queryset = FileGroupModel.objects.filter(document__id=pk)
        serializer = FileGroupSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

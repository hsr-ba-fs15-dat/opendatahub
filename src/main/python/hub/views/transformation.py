import re
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.db import transaction

from hub.serializers import FileGroupSerializer, TransformationSerializer
from hub.models import FileGroupModel, TransformationModel
from authentication.permissions import IsOwnerOrPublic, IsOwnerOrReadOnly
from hub.utils.common import str2bool


class TransformationViewSet(viewsets.ModelViewSet):
    queryset = TransformationModel.objects.all()
    serializer_class = TransformationSerializer
    paginate_by_param = 'count'
    paginate_by = 20
    permission_classes = IsOwnerOrPublic, IsOwnerOrReadOnly,

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

    def list(self, request, *args, **kwargs):
        """
        Search for transformations. Valid query parameters:
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
                out[m.group(1)][m.group(2)] = str2bool(v[0])
        if out:
            params.update(out)
        documents = TransformationModel.objects.all()

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

    @detail_route()
    def delete(self, request, pk):
        transformation = TransformationModel.objects.get(id=pk)
        transformation.delete()

        return Response()

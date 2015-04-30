import zipfile

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.http.response import JsonResponse
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponse
from django.utils.text import slugify

from opendatahub.utils.cache import cache
from hub.serializers import FileGroupSerializer, TransformationSerializer
from hub.models import FileGroupModel, TransformationModel
from authentication.permissions import IsOwnerOrPublic, IsOwnerOrReadOnly
from hub.views.mixins import FilterablePackageListViewSet
from hub.utils.odhql import TransformationUtil
from hub import formatters
from hub.formats import Format


class TransformationViewSet(viewsets.ModelViewSet, FilterablePackageListViewSet):
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

    @detail_route()
    def data(self, request, pk, *args, **kwargs):
        format_name = request.query_params.get('fmt', 'CSV')

        cache_key = ('transformation', 'data', pk, format_name)
        result_list = cache.L1.get(cache_key)

        model = TransformationModel.objects.get(id=pk)

        if not result_list:
            try:
                df = TransformationUtil.df_for_transformation(model)
            except:
                return JsonResponse({'error': 'File does not exist'}, status=HttpResponseNotFound.status_code)

            if df is None:
                return JsonResponse({'error': 'Transformation returned no data'},
                                    status=HttpResponseServerError.status_code)

            result_list = formatters.Formatter.format([df], slugify(unicode(model.name)),
                                                      Format.from_string(format_name))

        if not result_list:
            return JsonResponse({'error': 'Conversion failed', 'type': 'formatter'},
                                status=HttpResponseServerError.status_code)

        assert isinstance(result_list, (list, tuple))

        if request.is_ajax():
            cache.L1.set(cache_key, result_list)
            return JsonResponse({})  # just signal that it can be downloaded (200)

        response = HttpResponse()
        if len(result_list) > 1 or len(result_list) > 0 and len(result_list[0].files) > 1:
            response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(
                slugify(unicode(model.name))[:200])

            zip = zipfile.ZipFile(response, 'w')
            for result in result_list:
                for file in result:
                    zip.writestr(file.name, file.stream.getvalue())
            zip.close()
        else:
            file = result_list[0][0]
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(file.name)
            response.write(file.stream.getvalue())

        response['Content-Type'] = 'application/octet-stream'
        response.flush()

        return response

    @detail_route()
    def filegroup(self, request, pk, *args, **kwargs):
        queryset = FileGroupModel.objects.filter(document__id=pk)
        serializer = FileGroupSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

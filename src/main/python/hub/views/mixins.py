import zipfile

from django.db.models import Q
import re
from rest_framework import mixins, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from django.http.response import HttpResponse, HttpResponseServerError, HttpResponseNotFound, JsonResponse
from django.utils.text import slugify

from opendatahub.utils.cache import cache
from hub.formats.base import Format


class FilterablePackageListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
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
                out[m.group(1)][m.group(2)] = self.str2bool(v[0])

        if out:
            params.update(out)

        packages = self.get_queryset().filter(Q(owner = request.user.id) | Q(private = False))

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

    def str2bool(self, v):
        if v.lower() in ('true', 'false'):
            return v.lower() == 'true'
        return v


class DataDownloadMixin(viewsets.GenericViewSet):
    cache_prefix = None

    @detail_route()
    def data(self, request, pk, *args, **kwargs):
        format_name = request.query_params.get('fmt', 'CSV')

        cache_key = (self.cache_prefix, 'data', pk, format_name)
        result_list = cache.L1.get(cache_key)

        model = self.get_object()

        if not model:
            return JsonResponse({'error': 'Object does not exist'}, status=HttpResponseNotFound.status_code)

        if not result_list:
            result_list = self.format_object(model, Format.from_string(format_name))

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
                slugify(unicode(self.get_name(model)))[:200])

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

    def format_object(self, model, format):
        pass

    def get_name(self, model):
        pass

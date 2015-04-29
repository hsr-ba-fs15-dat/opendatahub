from django.db.models import Q
import re
from rest_framework import mixins, viewsets
from rest_framework.response import Response


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
        parameter_regex = re.compile("^(filter|sorting)\[(\w+)\]$")
        for k, v in params.iteritems():
            m = re.match(parameter_regex, k)
            if m:
                out[m.group(1)][m.group(2)] = self.str2bool(v[0])

        if out:
            params.update(out)

        packages = self.get_queryset().all()

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

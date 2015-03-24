from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from hub.formats.base import Format
from hub.serializers import FormatSerializer


class FormatView(ViewSet):
    def list(self, request):
        """Lists the available formats"""
        serializer = FormatSerializer([f for f in Format.formats.itervalues()], many=True)
        return Response(serializer.data)

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers

from hub.formatter import known_formatters


class FormatDescriptionSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    mime_type = serializers.CharField(read_only=True)


class FormatView(ViewSet):
    def list(self, request):
        """Lists the available formats"""
        serializer = FormatDescriptionSerializer([f.description for f in known_formatters.values()], many=True)
        return Response(serializer.data)
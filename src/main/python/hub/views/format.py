# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from hub.serializers import FormatSerializer


class FormatView(ViewSet):
    def list(self, request):
        """Lists the available formats"""
        from hub.formats import Formatter

        serializer = FormatSerializer([f for f in Formatter.formatters_by_target.keys()], many=True)
        return Response(serializer.data)

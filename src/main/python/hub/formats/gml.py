# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hub.formats import Format
from hub.utils import ogr2ogr

if 'GML' in ogr2ogr.SUPPORTED_DRIVERS:
    class GML(Format):
        label = 'GML'
        ogr_format = ogr2ogr.GML

        description = """
        Geometry Markup Language (GML) ist ein Dateiformat zum Austausch von Geodaten.
        """

        extension = 'gml'

        @classmethod
        def is_format(cls, file, *args, **kwargs):
            return file.extension == 'gml'

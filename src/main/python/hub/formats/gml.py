# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hub.formats import Format
from hub.formats.geobase import GenericOGRFormatter, GenericOGRParser
from hub.utils import ogr2ogr

if 'GML' in ogr2ogr.SUPPORTED_DRIVERS:
    class GML(Format):
        label = 'GML'
        ogr_format = ogr2ogr.GML

        description = """
        Geometry Markup Language (GML) ist ein Dateiformat zum Austausch von Geodaten.
        """

        extension = ogr_format.extension[0]

        @classmethod
        def is_format(cls, file, *args, **kwargs):
            return file.extension == cls.extension

    class GMLParser(GenericOGRParser):
        accepts = GML,

    class GMLFormatter(GenericOGRFormatter):
        targets = GML,

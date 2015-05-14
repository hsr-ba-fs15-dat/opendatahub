# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hub.formats import Format
from hub.utils import ogr2ogr


class GML(Format):
    label = 'GML'
    ogr_format = ogr2ogr.GML

    description = """
    Geometry Markup Language (GML) ist ein Dateiformat zum Austausch von Geodaten.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'gml'

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import geopandas as gp
import os

from hub.formats import Format, Parser
from hub.formats.geobase import GeoFormatterBase
from hub.utils import ogr2ogr

if 'ESRI Shapefile' in ogr2ogr.SUPPORTED_DRIVERS:
    class Shapefile(Format):
        label = 'ESRI Shapefile'
        ogr_format = ogr2ogr.SHP

        description = """
        Ein ursprünglich für die Firma ESRI entwickeltes Format für Geodaten.
        """

        extension = ogr_format.extension[0]

        @classmethod
        def is_format(cls, file, *args, **kwargs):
            return file.extension == cls.extension

    class ShapefileFormatter(GeoFormatterBase):
        targets = Shapefile,

        supported_types = {'Point', 'LineString', 'LinearRing', 'Polygon', 'MultiPoint'}

        @classmethod
        def format(cls, dfs, name, format, *args, **kwargs):
            return super(ShapefileFormatter, cls).format(dfs, name, format, Shapefile.ogr_format.identifier,
                                                         Shapefile.extension, *args, **kwargs)

    class ShapefileParser(Parser):
        accepts = Shapefile,

        @classmethod
        def parse(cls, file, format, *args, **kwargs):
            with file.file_group.on_filesystem() as temp_dir:
                return gp.read_file(os.path.join(temp_dir, file.name), driver=Shapefile.ogr_format.identifier)

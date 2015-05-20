# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import geopandas as gp
import os

from hub.formats.core import Format, Parser
from hub.formats.geobase import GeoFormatterBase


class GeoPackage(Format):
    label = 'GeoPackage'
    description = """
    Universelles Format für Vektor- und Raster-basierte Geo-Daten.
    """
    extension = 'gpkg'

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'gpkg'


class GeoPackageFormatter(GeoFormatterBase):
    targets = GeoPackage,
    """
    Formatter for GeoPackage files, a format based on sqlite.

    The GPKG speec does not allow non-spatial tables in non-extended GeoPackage, and GDAL does not support them
    at all before version 2.0 (http://www.gdal.org/drv_geopackage.html).
    """
    # targets = formats.GeoPackage,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        return super(GeoPackageFormatter, cls).format(dfs, name, format, 'GPKG', 'gpkg', *args, **kwargs)


class GeoPackageParser(Parser):
    accepts = GeoPackage,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        with file.file_group.on_filesystem() as temp_dir:
            return gp.read_file(os.path.join(temp_dir, file.name), driver='GPKG')

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hub.formats import Format
from hub.formats.geobase import GeoFormatterBase


class GeoPackage(Format):
    label = 'GeoPackage'
    description = """
    Universelles Format für Vektor- und Raster-basierte Geo-Daten.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'gpkg'


class GeoPackageFormatter(GeoFormatterBase):
    """
    Formatter for GeoPackage files, a format based on sqlite.

    The GPKG speec does not allow non-spatial tables, and GDAL does not support them before version 2.0
    (http://www.gdal.org/drv_geopackage.html).
    """
    # targets = formats.GeoPackage,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        return super(GeoPackageFormatter, cls).format(dfs, name, format, 'GPKG', 'gpkg', *args, **kwargs)

# class GeoPackageParser(Parser):
# accepts = formats.GeoPackage,
#
# @classmethod
# def parse(cls, file, format, *args, **kwargs):
# with file.file_group.on_filesystem() as temp_dir:
#             return gp.read_file(os.path.join(temp_dir, file.name), driver='GPKG')
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import shutil
import tempfile

import os
from shapely.geometry.base import GEOMETRY_TYPES

from hub.formats import Parser, Formatter
from hub.formats.gml import GML
# from hub.formats.interlis1 import INTERLIS1
from hub.formats.kml import KML
from hub.formats.wfs import WFS
from hub.formats.interlis1 import INTERLIS1
from hub.structures.file import FileGroup
from hub.utils import ogr2ogr


class GenericOGRParser(Parser):
    accepts = GML, WFS, INTERLIS1

    @classmethod
    def parse(cls, file, format, *args, **kwargs):

        # This currently uses ESRI Shapefile as intermediate format. That kinda sucks
        # (see http://giswiki.hsr.ch/Shapefile), but:
        # GeoJSON: doesn't support multiple layers
        # GeoPackage: ogr2ogr has no driver for that in our version
        # Interlis1: needs a model which we don't have
        # CSV: Yeah. Right.
        # GML, KML: Not supported by fiona so geopandas can't read it

        try:
            file_groups = ogr2ogr.ogr2ogr(file.file_group, ogr2ogr.KML, addtl_args=['-t_srs', 'EPSG:4326'],
                                          log_on_error=False)
        except ogr2ogr.Ogr2OgrException:
            file_groups = ogr2ogr.ogr2ogr(file.file_group, ogr2ogr.KML)

        dfs = []

        for fg in file_groups:
            main_file = fg.get_main_file()
            if main_file:
                dfs.extend(Parser.parse(main_file, KML, enforce_kml_attrs=False))

        return dfs


class GeoFormatterBase(Formatter):
    _is_abstract = True

    supported_types = set(GEOMETRY_TYPES)

    @classmethod
    def format(cls, dfs, name, format, driver, extension, *args, **kwargs):
        formatted = []

        for df in dfs:
            if df.has_geoms:
                gdf = df.to_gdf(supported_geoms=cls.supported_types)
                temp_dir = tempfile.mkdtemp()
                try:
                    gdf.to_file(os.path.join(temp_dir, df.name + '.{}'.format(extension)), driver=driver)
                    file_group = FileGroup.from_files(*[os.path.join(temp_dir, f) for f in os.listdir(temp_dir)])
                finally:
                    shutil.rmtree(temp_dir)
            else:
                formatted.extend(list(GenericOGRFormatter.format(dfs, name, format)))
                continue
                # formatted = list(Formatter.format(dfs, df.name, formats.CSV, *args, **kwargs))
                # file_group = ogr2ogr.ogr2ogr(formatted[0], ogr2ogr.CSV)[0]

            formatted.append(file_group)

        return formatted


class GenericOGRFormatter(Formatter):
    targets = GML, INTERLIS1

    # Note: Interlis 2 is not supported for export, because it would need a schema for that. Because it is the only
    # format with a schema requirement and adding that feature would mean investing a substantial amount of time we
    # don't currently have, we decided to not support exporting to Interlis 2 at this time.

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        formatted = []

        for fg in Formatter.format(dfs, name, KML, skip_kml_attrs=True, *args, **kwargs):
            formatted.extend(ogr2ogr.ogr2ogr(fg, format.ogr_format))

        return formatted

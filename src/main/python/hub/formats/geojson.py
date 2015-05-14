# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import geopandas as gp

from hub.formats import Format, Parser
from hub.utils import ogr2ogr
from hub.formats.geobase import GeoFormatterBase


class GeoJSON(Format):
    label = 'GeoJSON'
    ogr_format = ogr2ogr.GEO_JSON

    description = """
    GeoJSON ist ein Dateiformat zum Austausch von Geodaten mittels JSON.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'geojson' or (
            file.extension == 'json' and '"geometry"' in file)  # todo figure out a better way


class GeoJSONFormatter(GeoFormatterBase):
    targets = GeoJSON,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        return super(GeoJSONFormatter, cls).format(dfs, name, format, 'GeoJSON', 'json', *args, **kwargs)


class GeoJSONParser(Parser):
    accepts = GeoJSON,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        with file.file_group.on_filesystem() as temp_dir:
            return gp.read_file(os.path.join(temp_dir, file.name), driver='GeoJSON')

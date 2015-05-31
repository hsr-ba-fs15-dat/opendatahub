# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import geopandas as gp

from hub.formats import Format, Parser
from hub.structures.file import File
from hub.utils import ogr2ogr
from hub.formats.geobase import GeoFormatterBase


class GeoJSON(Format):
    label = 'GeoJSON'
    ogr_format = ogr2ogr.GEO_JSON

    description = """
    GeoJSON ist ein Dateiformat zum Austausch von Geodaten mittels JSON.
    """

    extension = 'geojson'

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == cls.extension or \
            (file.extension == cls.ogr_format.extension[0] and '"geometry"' in file)


class GeoJSONFormatter(GeoFormatterBase):
    targets = GeoJSON,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        formatted = []

        for df in dfs:
            if df.has_geoms:
                gdf = df.to_gdf(supported_geoms=cls.supported_types)
                formatted.append(
                    File.from_string(df.name + '.' + GeoJSON.ogr_format.extension[0], gdf.to_json()).file_group)
            else:
                formatted.append(
                    File.from_string(df.name + '.' + GeoJSON.ogr_format.extension[0],
                                     df.as_safe_serializable().to_json(orient='records')).file_group)

        return formatted


class GeoJSONParser(Parser):
    accepts = GeoJSON,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        with file.file_group.on_filesystem() as temp_dir:
            return gp.read_file(os.path.join(temp_dir, file.name), driver=GeoJSON.ogr_format.identifier)

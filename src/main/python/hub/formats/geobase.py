# -*- coding: utf-8 -*-
""" Base classes for format support based on ogr2ogr. """

from __future__ import unicode_literals

import shutil
import tempfile

import os

from shapely.geometry.base import GEOMETRY_TYPES

from hub.formats import Parser, Formatter
from hub.formats.csv import CSV

from hub.formats.kml import KML
from hub.structures.file import FileGroup
from hub.utils import ogr2ogr


class GenericOGRParser(Parser):
    """ Uses ogr2ogr as parser. """

    @classmethod
    def parse(cls, file, format, *args, **kwargs):

        # This uses an intermediate format which we know how to read/write independently from ogr2ogr. Then, ogr2ogr
        # can do the fun stuff like convert into formats we don't really know about. However, the choice of intermediate
        # format turns out not to be trivial. The following options exist:
        #
        # ESRI Shapefile: various issues (cuts off names, limited geometry support, etc.
        #   see http://giswiki.hsr.ch/Shapefile)
        # GeoJSON: doesn't support multiple layers
        # GeoPackage: ogr2ogr has no driver for that in version 1.10.x, the driver in 1.11.x sucks and 2.0.0
        #   is not released yet
        # Interlis1: No support in fiona
        # CSV: Yeah. Right.
        # GML: No support in fiona
        # KML: No support in fiona so geopandas can't read it. However, we implemented our own KML parser/
        #   formatter anyway, so KML it is.

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
    """ Base class for more convenient implementation of ogr2ogr-based formatters. """
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
                formatted.extend(list(cls.no_geometry_fallback(df, format, name)))
                continue
                # formatted = list(Formatter.format(dfs, df.name, formats.CSV, *args, **kwargs))
                # file_group = ogr2ogr.ogr2ogr(formatted[0], ogr2ogr.CSV)[0]

            formatted.append(file_group)

        return formatted

    @classmethod
    def no_geometry_fallback(cls, df, format, name):
        return GenericOGRFormatter.format([df], name, format)


class GenericOGRFormatter(Formatter):
    """ Uses ogr2ogr as formatter. """

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        from hub.formats.geojson import GeoJSON

        formatted = []

        for df in dfs:
            intermediate = GeoJSON if df.has_geoms else CSV
            for fg in Formatter.format([df], name, intermediate, *args, **kwargs):
                formatted.extend(ogr2ogr.ogr2ogr(fg, format.ogr_format))

        return formatted

# -*- coding: utf-8 -*-
from __future__ import unicode_literals


"""
"""

import logging
import collections
import traceback
import sys

import pandas as pd
import geopandas as gp
import os
import pygeoif.geometry
import fastkml.geometry
import shapely.geometry
from shapely.geometry.proxy import CachingGeometryProxy
from fiona.crs import from_epsg

from opendatahub.utils.plugins import RegistrationMixin
from hub import formats
from hub.utils import ogr2ogr
import hub.utils.common as com
from hub.structures.frame import OdhSeries, OdhType, OdhFrame
from osgeo import osr
import fiona.crs
import shapely.wkt
import re


logger = logging.getLogger(__name__)


class NoParserException(Exception):
    pass


class ParsingException(Exception):
    pass


class Parser(RegistrationMixin):
    _is_abstract = True
    parsers = {}
    parsers_by_format = collections.defaultdict(list)

    accepts = ()

    @classmethod
    def register_child(cls, name, bases, dct):
        if not dct.get('_is_abstract'):
            cls.parsers[name] = cls
            for format in cls.accepts:
                cls.parsers_by_format[format].append(cls)

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        exc_infos = []
        for parser in cls.parsers_by_format[format]:
            try:
                dfs = com.ensure_tuple(parser.parse(file, format=format, *args, **kwargs))
                dfs = [OdhFrame.from_df(df, getattr(df, 'name', file.basename)) for df in dfs]
                if not dfs:
                    raise ParsingException('Parser did not return DataFrames')

                assert all([df.name for df in dfs]), 'DataFrame must have a name'
                assert len(set([df.name for df in dfs])) == len(dfs), 'Duplicate DataFrame names'
                return dfs
            except:
                exc_infos.append(sys.exc_info())
                continue

        if exc_infos:
            tbs = '\n'.join([''.join(traceback.format_exception(*ei)) for ei in exc_infos])
            logger.error('No parser was able to parse %s with format %s\n%s', file.name, format.__name__, tbs)

        raise NoParserException('Unable to parse data')


class CSVParser(Parser):
    accepts = formats.CSV,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        return pd.read_csv(file.stream, encoding='UTF-8')


class JSONParser(Parser):
    accepts = formats.JSON,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        return pd.read_json(file.stream)


class ExcelParser(Parser):
    accepts = formats.Excel,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        return pd.read_excel(file.stream, encoding='UTF-8')


class KMLParser(Parser):
    accepts = formats.KML,

    @classmethod
    def proxy_to_obj(cls, proxy):
        res = proxy
        if isinstance(proxy, CachingGeometryProxy):
            res = getattr(shapely.geometry, proxy.geom_type)(proxy)
        return res

    @classmethod
    def _get_geoms(cls, geometry):
        if isinstance(geometry, pygeoif.GeometryCollection):
            result = {}
            for i, g in enumerate(geometry.geoms):
                col = 'geometry' + bool(i) * str((i + 1))
                result[col] = cls._get_geoms(g)['geometry']
            return result
        elif isinstance(geometry, pygeoif.geometry._Feature):
            return {'geometry': cls.proxy_to_obj(fastkml.geometry.Geometry(geometry=geometry).geometry)}

        return {'geometry': cls.proxy_to_obj(geometry)}

    @classmethod
    def parse(cls, file, format, enforce_kml_attrs=True, *args, **kwargs):

        kml = fastkml.KML()
        kml.from_string(file.stream.read())
        doc = next(kml.features())
        dfs = []

        for folder in doc.features():
            placemarks = list(folder.features())

            if placemarks:
                constructor = lambda: len(placemarks) * [None]
                data = collections.defaultdict(constructor)

                for i, placemark in enumerate(placemarks):
                    for key in ('id', 'name', 'description', 'address', 'author', 'begin', 'end'):
                        value = getattr(placemark, key, None)
                        if enforce_kml_attrs or value:
                            data[key][i] = value

                    if placemark.extended_data:
                        for v in placemark.extended_data.elements[0].data:
                            data[v['name']][i] = v['value']

                    if placemark._geometry:
                        for col, geom in cls._get_geoms(placemark.geometry).iteritems():
                            data[col][i] = geom

                df = OdhSeries.concat(
                    [OdhSeries(vals, name=name).convert_objects(convert_numeric=True) for name, vals in
                     data.iteritems()],
                    axis=1)

                for c, s in df.iteritems():
                    if s.odh_type == OdhType.GEOMETRY:
                        s.crs = from_epsg(4326)  # KML uses SRID 4326 by definition

                df.name = folder.name or file.basename
                dfs.append(df)

        return dfs


class GeoJSONParser(Parser):
    accepts = formats.GeoJSON,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        with file.file_group.on_filesystem() as temp_dir:
            return gp.read_file(os.path.join(temp_dir, file.name), driver='GeoJSON')


# class GeoPackageParser(Parser):
# accepts = formats.GeoPackage,
#
# @classmethod
#     def parse(cls, file, format, *args, **kwargs):
#         with file.file_group.on_filesystem() as temp_dir:
#             return gp.read_file(os.path.join(temp_dir, file.name), driver='GPKG')


class ShapefileParser(Parser):
    accepts = formats.Shapefile,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        with file.file_group.on_filesystem() as temp_dir:
            return gp.read_file(os.path.join(temp_dir, file.name), driver='ESRI Shapefile')


class GenericOGRParser(Parser):
    accepts = formats.GML, formats.INTERLIS1, formats.WFS

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
                dfs.extend(Parser.parse(main_file, formats.KML, enforce_kml_attrs=False))

        return dfs


class GenericXMLParser(Parser):
    """ Flat XML parser
    """

    accepts = formats.XML,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        from lxml import etree

        et = etree.parse(file.stream)
        return pd.DataFrame([dict(text=e.text, **e.attrib) for e in et.getroot()])


class GeoCSVParser(Parser):
    accepts = formats.GeoCSV,

    CSVT_RE = re.compile('\s*(\w+)\s*\(.*\)\s*', re.IGNORECASE)

    @classmethod
    def _parse_prj(cls, fg):
        prjs = fg.get_by_extension('prj')
        if prjs:
            prj = prjs[0]
            srs = osr.SpatialReference()

            srs.ImportFromESRI([prj.ustream.read()])
            return fiona.crs.from_string(srs.ExportToProj4())

        return {}

    @classmethod
    def _parse_csvt(cls, fg):
        csvts = fg.get_by_extension('csvt')
        if csvts:
            csvt = csvts[0]
            fields = csvt.stream.readline().split(';')
            try:
                return [cls.CSVT_RE.match(f).group(1).lower() for f in fields]
            except (AttributeError, IndexError) as e:
                logger.warn('Could not parse CSVT file "%s": %s', csvt.stream.read(), e.message)

        return ()

    @classmethod
    def _parse_csv(cls, fg):
        csv = fg.get_by_extension('csv')[0]
        return OdhFrame.from_df(pd.read_csv(csv.ustream, encoding='UTF-8', sep=';'))

    @classmethod
    def _parse_integer(cls, i, s, df, types):
        return OdhType.INTEGER.convert(s)

    @classmethod
    def _parse_string(cls, i, s, df, types):
        return OdhType.TEXT.convert(s)

    @classmethod
    def _parse_real(cls, i, s, df, types):
        return OdhType.FLOAT.convert(s)

    @classmethod
    def _parse_date(cls, i, s, df, types):
        return pd.to_datetime(s, infer_datetime_format=True)  # format='%Y-%m-%d'

    @classmethod
    def _parse_time(cls, i, s, df, types):
        return pd.to_datetime(s, infer_datetime_format=True)  # format='%H:%M:%S'

    @classmethod
    def _parse_datetime(cls, i, s, df, types):
        return pd.to_datetime(s, infer_datetime_format=True)  # format='%Y-%m-%d %H:%M:%S'

    @classmethod
    def _parse_wkt(cls, i, s, df, types):
        s = s.apply(shapely.wkt.loads, convert_dtype=False)
        s.crs = df.crs
        return s

    @classmethod
    def _parse_easting(cls, ix, s, df, types):
        if ix > 0 and types[ix - 1] != 'Northing':
            iy = types[ix:].index('Northing')
            return cls._parse_point(df, ix, iy)

    @classmethod
    def _parse_northing(cls, iy, s, df, types):
        if iy > 0 and types[iy - 1] != 'Easting':
            ix = types[iy:].index('Easting')
            return cls._parse_point(df, ix, iy)

    @classmethod
    def _parse_point(cls, df, ix, iy):
        s = OdhType.FLOAT.convert(df.iloc[:, [ix, iy]]).apply(shapely.geometry.Point, axis=1)
        s.crs = df.crs
        return s

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        fg = file.file_group

        crs = cls._parse_prj(fg)
        types = cls._parse_csvt(fg)
        df = cls._parse_csv(fg)
        df.crs = crs

        if types:
            assert len(df.columns) == len(types)

            series = []
            for i, (c, s) in enumerate(df.iteritems()):
                type_ = types[i]
                parse_method = getattr(cls, '_parse_' + type_.lower(), None)
                if not parse_method:
                    raise ParsingException('Unknown GeoCSV type "{}"'.format(type_))
                series.append(parse_method(i, s, df, types))

            df = OdhSeries.concat([s for s in series if s is not None], axis=1)

        return df

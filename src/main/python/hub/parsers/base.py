# -*- coding: utf-8 -*-

"""
"""

import logging
import collections

import pandas
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
        for parser in cls.parsers_by_format[format]:
            try:
                dfs = com.ensure_tuple(parser.parse(file, format=format, *args, **kwargs))
                dfs = [OdhFrame.from_df(df, file.basename) for df in dfs]
                if not dfs:
                    raise ParsingException('Parser did not return DataFrames')
                return dfs
            except:
                logging.debug('%s was not able to parse data with format %s', parser.__name__, format.__name__,
                              exc_info=True)
                continue

        raise NoParserException('Unable to parse data')


class CSVParser(Parser):
    accepts = formats.CSV,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        return pandas.read_csv(file.stream, encoding='UTF-8')


class JSONParser(Parser):
    accepts = formats.JSON,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        return pandas.read_json(file.stream)


class ExcelParser(Parser):
    accepts = formats.Excel,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        return pandas.read_excel(file.stream, encoding='UTF-8')


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
    def parse(cls, file, format, *args, **kwargs):

        kml = fastkml.KML()
        kml.from_string(file.stream.read())
        doc = next(kml.features())
        folder = next(doc.features())
        placemarks = list(folder.features())

        constructor = lambda: len(placemarks) * [None]
        data = collections.defaultdict(constructor)

        for i, placemark in enumerate(placemarks):
            data['id'][i] = placemark.id
            data['name'][i] = placemark.name
            data['description'][i] = placemark.description
            data['address'][i] = placemark.address
            data['author'][i] = placemark.author
            data['begin'][i] = placemark.begin
            data['end'][i] = placemark.end
            if placemark.extended_data:
                for v in placemark.extended_data.elements[0].data:
                    data[v['name']][i] = v['value']

            if placemark.geometry:
                for col, geom in cls._get_geoms(placemark.geometry).iteritems():
                    data[col][i] = geom

        df = OdhSeries.concat(
            [OdhSeries(vals, name=name).convert_objects(convert_numeric=True) for name, vals in data.iteritems()],
            axis=1)
        for c, s in df.iteritems():
            if s.odh_type == OdhType.GEOMETRY:
                s.crs = from_epsg(4326)  # KML uses SRID 4326 by definition

        return df


class GeoJSONParser(Parser):
    accepts = formats.GeoJSON,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        with file.file_group.on_filesystem() as temp_dir:
            return gp.read_file(os.path.join(temp_dir, file.name), driver='GeoJSON')


class GeoPackageParser(Parser):
    accepts = formats.GeoPackage,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        with file.file_group.on_filesystem() as temp_dir:
            return gp.read_file(os.path.join(temp_dir, file.name), driver='GPKG')


class ShapefileParser(Parser):
    accepts = formats.Shapefile,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        with file.file_group.on_filesystem() as temp_dir:
            return gp.read_file(os.path.join(temp_dir, file.name), driver='ESRI Shapefile')


class OGRParser(Parser):
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

        file_groups = ogr2ogr.ogr2ogr(file.file_group, ogr2ogr.SHP)

        dataframes = []

        for group in file_groups:
            with group.on_filesystem() as temp_dir:
                main_file = group.get_main_file()
                if main_file:
                    dataframes.append(gp.read_file(os.path.join(temp_dir, main_file.name)))

        return dataframes


class GenericXMLParser(Parser):
    """ Flat XML parser
    """

    accepts = formats.XML,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        from lxml import etree

        et = etree.parse(file.stream)
        return pandas.DataFrame([dict(text=e.text, **e.attrib) for e in et.getroot()])

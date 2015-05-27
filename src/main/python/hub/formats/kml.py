# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import logging

import fastkml
from fiona.crs import from_epsg
from lxml.etree import CDATA
import pygeoif
import shapely
from shapely.geometry.proxy import CachingGeometryProxy

from hub.formats import Format, Formatter, Parser
from hub.structures.file import File
from hub.structures.frame import OdhType, OdhSeries
from hub.utils import ogr2ogr

from hub.exceptions import warn

from hub.utils.common import ensure_tuple

logger = logging.getLogger(__name__)


class KML(Format):
    label = 'KML'
    ogr_format = ogr2ogr.KML

    description = """
    Keyhole Markup Language (KML) ist ein Dateiformat zum Austausch von Geodaten. KML wurde durch die Verwendung in
    Google Earth bekannt.
    """

    extension = 'kml'

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'kml'


class KMLFormatter(Formatter):
    targets = KML,

    KML_ATTRS = ('name', 'description', 'address', 'author', 'begin', 'end')

    TYPE_MAP = {
        OdhType.INTEGER: 'int',
        OdhType.SMALLINT: 'short',
        OdhType.BIGINT: 'int',
        OdhType.DATETIME: 'string',
        OdhType.INTERVAL: 'string',
        OdhType.TEXT: 'string',
        OdhType.BOOLEAN: 'bool',
        OdhType.FLOAT: 'float',
    }

    CRS = from_epsg(4326)

    @classmethod
    def _create_schema(cls, df, skip_kml_attrs):
        schema = fastkml.Schema(fastkml.config.NS, df.name, df.name)
        for c, s in df.iteritems():
            if c not in cls.KML_ATTRS or skip_kml_attrs:
                try:
                    type_ = cls.TYPE_MAP[s.odh_type]
                except KeyError:
                    logger.warn('Unknown type %s for KML schema generation, using string.', c.odh_type)
                    type_ = 'string'

                schema.append(type_, c)
        return schema

    @classmethod
    def format(cls, dfs, name, format, skip_kml_attrs=True, *args, **kwargs):
        kml = fastkml.KML()
        ns = fastkml.config.NS
        doc = fastkml.Document(ns, name, kwargs.get('name'), kwargs.get('description'))
        kml.append(doc)

        for i, df in enumerate(dfs):
            df_attrs = df.loc[:, ensure_tuple([c for c in df if df[c].odh_type != OdhType.GEOMETRY])]
            df_geoms = df.loc[:, ensure_tuple([c for c in df if df[c].odh_type == OdhType.GEOMETRY])]

            df_geoms_copy = df_geoms.copy()

            for c, s in df_geoms.iteritems():
                # assigning a series to a dataframe 'sanitizes' away the crs, so we need to dance around that
                if not s.crs:
                    warn('The column "{}" does not have a valid coordinate reference system (CRS) set. As KML requires'
                         ' EPSG 4326 to be used, this may lead to an invalid file.'.format(c))
                    s_new = s
                else:
                    s_new = s.to_crs(cls.CRS)

                df_geoms_copy[c] = s_new

                df_geoms_copy.__finalize__(df_geoms)
                df_geoms_copy[c].__finalize__(s_new)

            df_geoms = df_geoms_copy

            folder = fastkml.Folder(ns, str(i), df.name)
            doc.append(folder)
            doc.append_schema(cls._create_schema(df_attrs, skip_kml_attrs=skip_kml_attrs))
            schema_url = '#' + df.name

            for i, row in df_attrs.iterrows():
                placemark = fastkml.Placemark(ns)
                folder.append(placemark)
                row = row.to_dict()

                if not skip_kml_attrs:
                    id_ = str(row.pop('id', i))
                    placemark.id = id_

                    for key in cls.KML_ATTRS:
                        value = row.pop(key, None)
                        if value:
                            setattr(placemark, key, CDATA(unicode(value)))

                if row:
                    properties = [{'name': unicode(k), 'value': v if v is None else CDATA(unicode(v))} for k, v in
                                  row.iteritems()]
                    schema_data = fastkml.SchemaData(ns, schema_url, properties)
                    extended_data = fastkml.ExtendedData(ns, [schema_data])

                    placemark.extended_data = extended_data

                geoms = [g for g in df_geoms.ix[i].values if g]
                geometry = None
                if len(geoms) == 1:
                    geometry = geoms[0]
                elif len(geoms) > 1:
                    geometry = pygeoif.GeometryCollection(geoms)

                if geometry:
                    placemark.geometry = geometry

        return [File.from_string(name + '.kml', kml.to_string()).file_group]


class KMLParser(Parser):
    accepts = KML,

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

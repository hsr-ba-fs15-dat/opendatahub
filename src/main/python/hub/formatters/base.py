# -*- coding: utf-8 -*-

"""
"""

import collections
import tempfile
import shutil
import logging
from lxml import etree

import os
import pygeoif
from lxml.etree import CDATA
import fastkml
import fastkml.config

from opendatahub.utils.plugins import RegistrationMixin
from hub import formats
from hub.structures.file import File, FileGroup
from hub.utils import ogr2ogr
from hub.structures.frame import OdhType
import hub.utils.common as com


logger = logging.getLogger(__name__)


class NoFormatterException(Exception):
    pass


class FormattingException(Exception):
    pass


class Formatter(RegistrationMixin):
    _is_abstract = True

    formatters = {}
    formatters_by_target = collections.defaultdict(list)

    targets = ()

    @classmethod
    def register_child(cls, name, bases, dct):
        if not dct.get('_is_abstract'):
            cls.formatters[name] = cls
            for format in cls.targets:
                cls.formatters_by_target[format].append(cls)

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        for formatter in cls.formatters_by_target[format]:
            try:
                result = com.ensure_tuple(formatter.format(dfs, name, format=format, *args, **kwargs))
                if not result:
                    raise FormattingException('Formatter did not return any result')
                return result
            except:
                logger.debug('%s was not able to format %s with target format %s', formatter.__name__, file.name,
                             format.__name__, exc_info=True)
                continue

        raise NoFormatterException('Unable to format {} as {}'.format(file.name, format.name))


class CSVFormatter(Formatter):
    targets = formats.CSV,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        results = []

        for df in dfs:
            results.append(File.from_string(name + '.csv', df.to_csv(index=False, encoding='UTF-8')).file_group)
        return results


class JSONFormatter(Formatter):
    targets = formats.JSON,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        results = []

        for df in dfs:
            results.append(File.from_string(name + '.json', df.to_json(orient='records')).file_group)
        return results


class ExcelFormatter(Formatter):
    targets = formats.Excel,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        results = []

        for df in dfs:
            with tempfile.NamedTemporaryFile(suffix=".xlsx") as f:
                df.to_excel(f.name, engine='xlsxwriter', index=False)
                f.seek(0)
                results.append(File.from_string(name + '.xlsx', f.read()).file_group)
        return results


class XMLFormatter(Formatter):
    targets = formats.XML,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        results = []

        for df in dfs:
            root = etree.Element('root')
            for i, row in df.iterrows():
                etree.SubElement(root, 'row', row.dropna().astype(unicode).to_dict())

            results.append(File.from_string(name + '.xml',
                                            etree.tostring(root, encoding='UTF-8', xml_declaration=True,
                                                           pretty_print=True)).file_group)
        return results


class GeoFormatterBase(Formatter):
    _is_abstract = True

    @classmethod
    def format(cls, dfs, name, format, driver, extension, *args, **kwargs):
        formatted = []

        for df in dfs:
            if df.has_geoms:
                gdf = df.to_gdf()
                temp_dir = tempfile.mkdtemp()
                try:
                    gdf.to_file(os.path.join(temp_dir, name + '.{}'.format(extension)), driver=driver)
                    file_group = FileGroup.from_files(*[os.path.join(temp_dir, f) for f in os.listdir(temp_dir)])
                finally:
                    shutil.rmtree(temp_dir)
            else:
                formatted = Formatter.format(file, formats.CSV, *args, **kwargs)
                file_group = ogr2ogr.ogr2ogr(formatted[0], ogr2ogr.CSV)[0]

            formatted.append(file_group)

        return formatted


class GeoJSONFormatter(GeoFormatterBase):
    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        super(GeoJSONFormatter, cls).format(dfs, name, format, 'GeoJSON', 'json', *args, **kwargs)


class ShapefileFormatter(GeoFormatterBase):
    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        super(ShapefileFormatter, cls).format(dfs, name, format, 'ESRI Shapefile', 'shp', *args, **kwargs)


class KMLFormatter(Formatter):
    targets = formats.KML,

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
            df_attrs = df[[c for c in df if df[c].odh_type != OdhType.GEOMETRY]]
            df_geoms = df[[c for c in df if df[c].odh_type == OdhType.GEOMETRY]]

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


class GenericOGRFormatter(Formatter):
    targets = formats.GML, formats.INTERLIS1,

    # Note: Interlis 2 is not supported for export, because it would need a schema for that. Because it is the only
    # format with a schema requirement and adding that feature would mean investing a substantial amount of time we
    # don't currently have, we decided to not support exporting to Interlis 2 at this time.

    FORMAT_TO_OGR = {
        formats.GML: ogr2ogr.GML,
        formats.KML: ogr2ogr.KML,
        formats.Shapefile: ogr2ogr.SHP,
        formats.INTERLIS1: ogr2ogr.INTERLIS_1,
        # formats.GeoPackage: ogr2ogr.GPKG
    }

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        formatted = []

        for fg in Formatter.format(dfs, name, formats.KML, skip_kml_attrs=True, *args, **kwargs):
            formatted.extend(ogr2ogr.ogr2ogr(fg, cls.FORMAT_TO_OGR[format]))

        return formatted

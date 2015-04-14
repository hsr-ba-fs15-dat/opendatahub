# -*- coding: utf-8 -*-

"""
"""

import logging
import collections

import pandas
import geopandas
import os

from opendatahub.utils.plugins import RegistrationMixin
from hub import formats
from hub.utils import ogr2ogr
from hub.utils import cache
import traceback


class NoParserException(Exception):
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
    def parse(cls, file, format, force=False, *args, **kwargs):
        id_ = file.file_group.id
        df = None
        invalidate = False

        cache.get(id_)
        if not force and id_:
            df = cache.get(id_)

        if df is None:
            for parser in cls.parsers_by_format[format]:
                try:
                    df = parser.parse(file, format=format, *args, **kwargs)
                    invalidate = True
                    break
                except:
                    logging.debug('%s was not able to parse data with format %s: %s', parser.__name__, format.__name__,
                                  traceback.format_exc())
                    continue

        if df is None:
            raise NoParserException('Unable to parse data')

        if id_ and invalidate:
            cache.set(id_, df)

        return df


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


class OGRParser(Parser):
    accepts = formats.GML, formats.GeoJSON, formats.KML, formats.Shapefile

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        file_group = file.file_group
        name = file.name

        if format not in (formats.Shapefile, formats.GeoJSON):
            file_group = ogr2ogr.ogr2ogr(file_group, ogr2ogr.SHP)
            name = '{}.{}'.format(file.basename, ogr2ogr.SHP.extension)

        with file_group.on_filesystem() as temp_dir:
            return geopandas.read_file(os.path.join(temp_dir, name))


class GenericXMLParser(Parser):
    """ Flat XML parser
    """

    accepts = formats.XML,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        from lxml import etree

        et = etree.parse(file.stream)
        return pandas.DataFrame([dict(text=e.text, **e.attrib) for e in et.getroot()])

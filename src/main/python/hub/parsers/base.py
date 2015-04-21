# -*- coding: utf-8 -*-

"""
"""

import logging
import collections
import traceback

import pandas

import geopandas
import os

from opendatahub.utils.plugins import RegistrationMixin

from hub import formats
from hub.utils import ogr2ogr
import hub.utils.common as com
from hub.structures.frame import OdhFrame


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
    def parse(cls, file, format, *args, **kwargs):
        for parser in cls.parsers_by_format[format]:
            try:
                dfs = com.ensure_tuple(parser.parse(file, format=format, *args, **kwargs))
                return [OdhFrame.from_df(df, file.basename) for df in dfs]
            except:
                logging.debug('%s was not able to parse data with format %s: %s', parser.__name__, format.__name__,
                              traceback.format_exc())
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


class OGRParser(Parser):
    accepts = formats.GML, formats.GeoJSON, formats.KML, formats.Shapefile, formats.INTERLIS1,  # formats.INTERLIS2

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        if format in (formats.Shapefile, formats.GeoJSON):
            file_groups = [file.file_group]
        else:
            file_groups = ogr2ogr.ogr2ogr(file.file_group, ogr2ogr.SHP)

        dataframes = []

        for group in file_groups:
            with group.on_filesystem() as temp_dir:
                main_file = group.get_main_file()
                if main_file:
                    try:
                        dataframes.append(geopandas.read_file(os.path.join(temp_dir, main_file.name)))
                    except AttributeError:
                        pass

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

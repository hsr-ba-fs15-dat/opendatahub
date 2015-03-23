# -*- coding: utf-8 -*-

"""
"""

import pandas
import geopandas
import logging

import collections
import os
from opendatahub.utils.plugins import RegistrationMixin
from hub import formats
from hub.utils import ogr2ogr


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
                return parser.parse(file, format=format, *args, **kwargs)
            except:
                logging.debug('%s was not able to parse data with format %s', parser.__name__, format.__name__)
                continue

        raise NoParserException('Unable to parse data')


class CSVParser(Parser):
    accepts = formats.CSV,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        return pandas.read_csv(file.stream)


class JSONParser(Parser):
    accepts = formats.JSON,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        return pandas.read_json(file.stream)


class ExcelParser(Parser):
    accepts = formats.Excel,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        return pandas.read_excel(file.stream)


class OGRParser(Parser):
    accepts = formats.GML,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        file_group = file.file_group
        name = file.name

        if format not in (formats.Shapefile, formats.GeoJSON):
            file_group = ogr2ogr.ogr2ogr(file_group, ogr2ogr.SHP)
            name = '{}.{}'.format(os.path.splitext(name)[0], ogr2ogr.SHP.extension)

        with file_group.on_filesystem() as temp_dir:
            return geopandas.read_file(os.path.join(temp_dir, name))


if __name__ == '__main__':
    from hub.tests.testutils import TestBase
    from hub.structures.file import FileGroup

    files = (
        ('mockaroo.com.csv', formats.CSV),
        ('mockaroo.com.json', formats.JSON),
        ('gml/Bahnhoefe.gml', formats.GML),
        ('mockaroo.com.xls', formats.Excel),
    )

    print formats.Format.formats
    for filename, cls in files:
        fg = FileGroup.from_files(TestBase.get_test_file_path(filename))
        identified_formats = [formats.identify(f) for f in fg]
        assert cls in identified_formats

        f = fg[0]
        df = Parser.parse(f, cls)

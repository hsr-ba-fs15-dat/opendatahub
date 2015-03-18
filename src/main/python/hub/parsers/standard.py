# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
"""

import pandas
import logging

import collections
from opendatahub.utils.plugins import RegistrationMixin
from hub import formats


class NoParserException(Exception):
    pass


class Parser(RegistrationMixin):
    _is_abstract = True
    parsers = {}
    parsers_by_format = collections.defaultdict(list)

    @classmethod
    def register_child(cls, name, bases, dct):
        if not dct.get('_is_abstract'):
            cls.parsers[name] = cls
            for format in cls.accepts:
                cls.parsers_by_format[format].append(cls)

    @classmethod
    def parse(cls, stream, format=None, *args, **kwargs):
        if not format:
            format = formats.identify(stream, *args, **kwargs)

        for parser in cls.parsers_by_format[format]:
            try:
                return parser.parse(stream, format=format, *args, **kwargs)
            except:
                logging.debug('%s was not able to parse data with format %s', parser.__name__, format.__name__)
                continue

        raise NoParserException('Unable to parse data')


class CSVParser(Parser):
    accepts = formats.CSV,

    @classmethod
    def parse(cls, stream, format, *args, **kwargs):
        return pandas.read_csv(stream)


class JSONParser(Parser):
    accepts = formats.JSON,

    @classmethod
    def parse(cls, stream, format, *args, **kwargs):
        return pandas.read_json(stream)


class ExcelParser(Parser):
    accepts = formats.Excel,

    @classmethod
    def parse(cls, stream, format, *args, **kwargs):
        return pandas.read_excel(stream)


if __name__ == '__main__':

    from hub.tests.testutils import TestBase

    print Parser.parsers_by_format

    files = (
        ('mockaroo.com.csv', formats.CSV),
        ('mockaroo.com.json', formats.JSON),
        ('mockaroo.com.xls', formats.Excel),
    )

    print formats.Format.formats
    for filename, cls in files:
        with open(TestBase.get_test_file_path(filename)) as f:
            format = formats.identify(f, name=f.name)
            assert format == cls, (format, cls)

    for filename, cls in files:
        with open(TestBase.get_test_file_path(filename)) as f:
            df = Parser.parse(f, name=f.name)
            print df

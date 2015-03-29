# -*- coding: utf-8 -*-

"""
"""

import collections
import tempfile
import shutil
import logging
from lxml import etree

import geopandas
import pandas
import os

from opendatahub.utils.plugins import RegistrationMixin
from hub import formats
from hub.structures.file import File, FileGroup
from hub.utils import ogr2ogr


class NoFormatterException(Exception):
    pass


class FormattingException(Exception):
    pass


class Formatter(RegistrationMixin):
    _is_abstract = True

    formatters = {}
    formatters_by_tagret = collections.defaultdict(list)

    targets = ()

    @classmethod
    def register_child(cls, name, bases, dct):
        if not dct.get('_is_abstract'):
            cls.formatters[name] = cls
            for format in cls.targets:
                cls.formatters_by_tagret[format].append(cls)

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        for formatter in cls.formatters_by_tagret[format]:
            try:
                return formatter.format(file, format=format, *args, **kwargs)
            except:
                logging.debug(
                    '{} was not able to format {} with target format {}'.format(formatter.__name__, file.name,
                                                                                format.__name__))
                continue

        raise NoFormatterException('Unable to format {} as {}'.format(file.name, format.name))


class CSVFormatter(Formatter):
    targets = formats.CSV,

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        return File.from_string(file.basename + '.csv',
                                file.to_normalized_df().to_csv(index=False, encoding='UTF-8')).file_group


class JSONFormatter(Formatter):
    targets = formats.JSON,

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        return File.from_string(file.basename + '.json',
                                file.to_normalized_df().to_json(orient='records')).file_group


class ExcelFormatter(Formatter):
    targets = formats.Excel,

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as f:
            file.to_normalized_df().to_excel(f.name, engine='xlsxwriter', index=False)
            f.seek(0)
            return File.from_string(file.basename + '.xlsx', f.read()).file_group


class XMLFormatter(Formatter):
    targets = formats.XML,

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        df = file.to_normalized_df()
        root = etree.Element('root', {'origin': ', '.join(file.file_group.names)})
        for i, row in df.iterrows():
            etree.SubElement(root, 'row', row.dropna().astype(unicode).to_dict())

        return File.from_string(file.basename + '.xml', etree.tostring(root, encoding='UTF-8', xml_declaration=True,
                                                                       pretty_print=True)).file_group


class NoopFormatter(Formatter):
    targets = formats.Other,

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        return file.file_group


class OGRFormatter(Formatter):
    targets = formats.GeoJSON, formats.GML, formats.KML, formats.Shapefile

    FORMAT_TO_OGR = {
        formats.GeoJSON: ogr2ogr.GEO_JSON,
        formats.GML: ogr2ogr.GML,
        formats.KML: ogr2ogr.KML,
        formats.Shapefile: ogr2ogr.SHP,
    }

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        df = file.to_df()

        if isinstance(df, geopandas.GeoDataFrame):
            temp_dir = tempfile.mkdtemp()
            try:
                df.to_file(os.path.join(temp_dir, file.basename + '.shp'))
                file_group = FileGroup.from_files(*[os.path.join(temp_dir, f) for f in os.listdir(temp_dir)])
            finally:
                shutil.rmtree(temp_dir)
        elif isinstance(df, pandas.DataFrame):
            file = CSVFormatter.format(file, formats.CSV)
            file_group = ogr2ogr.ogr2ogr(file, ogr2ogr.CSV)
        else:
            raise FormattingException('Could not format {}'.format(df))

        return ogr2ogr.ogr2ogr(file_group, cls.FORMAT_TO_OGR[format])

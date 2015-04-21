# -*- coding: utf-8 -*-

"""
"""

import collections
import tempfile
import shutil
import logging
from lxml import etree
import traceback

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
    formatters_by_target = collections.defaultdict(list)

    targets = ()

    @classmethod
    def register_child(cls, name, bases, dct):
        if not dct.get('_is_abstract'):
            cls.formatters[name] = cls
            for format in cls.targets:
                cls.formatters_by_target[format].append(cls)

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        for formatter in cls.formatters_by_target[format]:
            try:
                return formatter.format(file, format=format, *args, **kwargs)
            except:
                logging.debug('%s was not able to format %s with target format %s: %s', formatter.__name__, file.name,
                              format.__name__, traceback.format_exc())
                continue

        raise NoFormatterException('Unable to format {} as {}'.format(file.name, format.name))


class CSVFormatter(Formatter):
    targets = formats.CSV,

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        dataframes = file.to_serializable_df()
        results = []

        for df in dataframes:
            results.append(
                File.from_string(file.basename + '.csv', df.to_csv(index=False, encoding='UTF-8')).file_group)
        return results


class JSONFormatter(Formatter):
    targets = formats.JSON,

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        dataframes = file.to_serializable_df()
        results = []

        for df in dataframes:
            results.append(File.from_string(file.basename + '.json', df.to_json(orient='records')).file_group)
        return results


class ExcelFormatter(Formatter):
    targets = formats.Excel,

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        dataframes = file.to_serializable_df()
        results = []

        for df in dataframes:
            with tempfile.NamedTemporaryFile(suffix=".xlsx") as f:
                df.to_excel(f.name, engine='xlsxwriter', index=False)
                f.seek(0)
                results.append(File.from_string(file.basename + '.xlsx', f.read()).file_group)
        return results


class XMLFormatter(Formatter):
    targets = formats.XML,

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        dataframes = file.to_serializable_df()
        results = []

        for df in dataframes:
            root = etree.Element('root', {'origin': ', '.join(file.file_group.names)})
            for i, row in df.iterrows():
                etree.SubElement(root, 'row', row.dropna().astype(unicode).to_dict())

            results.append(File.from_string(file.basename + '.xml',
                                            etree.tostring(root, encoding='UTF-8', xml_declaration=True,
                                                           pretty_print=True)).file_group)
        return results


class NoopFormatter(Formatter):
    targets = formats.Other,

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        return [file.file_group]


class OGRFormatter(Formatter):
    targets = formats.GeoJSON, formats.GML, formats.KML, formats.Shapefile, formats.INTERLIS1

    # Note: Interlis 2 is not supported for export, because it would need a schema for that. Because it is the only
    # format with a schema requirement and adding that feature would mean investing a substantial amount of time we
    # don't currently have, we decided to not support exporting to Interlis 2 at this time.

    FORMAT_TO_OGR = {
        formats.GeoJSON: ogr2ogr.GEO_JSON,
        formats.GML: ogr2ogr.GML,
        formats.KML: ogr2ogr.KML,
        formats.Shapefile: ogr2ogr.SHP,
        formats.INTERLIS1: ogr2ogr.INTERLIS_1
    }

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        dataframes = file.to_df()
        results = []

        for df in dataframes:
            if df.has_geoms:
                df = df.to_gdf()
                temp_dir = tempfile.mkdtemp()
                try:
                    df.to_file(os.path.join(temp_dir, file.basename + '.shp'))
                    file_group = FileGroup.from_files(*[os.path.join(temp_dir, f) for f in os.listdir(temp_dir)])
                finally:
                    shutil.rmtree(temp_dir)
            elif isinstance(df, pandas.DataFrame):
                formatted = CSVFormatter.format(file, formats.CSV)
                assert len(formatted) == 1, "formatting a single data frame as csv should only result in 1 file"
                file_group = ogr2ogr.ogr2ogr(formatted[0], ogr2ogr.CSV)[0]
            else:
                raise FormattingException('Could not format {}'.format(df))

            results.extend(ogr2ogr.ogr2ogr(file_group, cls.FORMAT_TO_OGR[format]))

        return results

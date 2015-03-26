# -*- coding: utf-8 -*-

"""
"""

import collections
import tempfile
import shutil

import geopandas
import pandas
import os

from opendatahub.utils.plugins import RegistrationMixin
from hub import formats
from hub.structures.file import File
from hub.utils import ogr2ogr


class NoFormatterException(Exception):
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
                raise
                # logging.debug('%s was not able to format data with target format %s', formatter.__name__,
                # format.__name__)
                # continue

        raise NoFormatterException('Unable to format data')


class CSVFormatter(Formatter):
    targets = formats.CSV,

    @classmethod
    def format(cls, file, format, *args, **kwargs):
        return File.from_string(file.basename + '.csv',
                                file.to_df().to_csv(index=False, encoding='UTF-8')).file_group


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

        if isinstance(df, pandas.DataFrame):
            file = CSVFormatter.format(file, formats.CSV)
            file_group = ogr2ogr.ogr2ogr(file, ogr2ogr.CSV)
        elif isinstance(df, geopandas.GeoDataFrame):
            temp_dir = tempfile.mkdtemp()
            try:
                df.to_file(os.path.join(temp_dir, file.basename + '.shp'))
                file_group = FileGroup.from_files(*os.listdir(temp_dir))
            except:
                # todo exception handling
                return None
            finally:
                shutil.rmtree(temp_dir)
        else:
            # todo exception handling
            return None

        return ogr2ogr.ogr2ogr(file_group, cls.FORMAT_TO_OGR[format])


if __name__ == '__main__':
    from hub.tests.testutils import TestBase
    from hub.structures.file import FileGroup

    files = (
        ('mockaroo.com.csv', formats.CSV),
        ('mockaroo.com.json', formats.JSON),
        ('gml/Bahnhoefe.gml', formats.GML),
        ('mockaroo.com.xls', formats.Excel),
    )

    for filename, cls in files:
        fg = FileGroup.from_files(TestBase.get_test_file_path(filename))

        f = fg[0]
        df = f.to_df()

        f = Formatter.format(f, formats.Excel)

        pass

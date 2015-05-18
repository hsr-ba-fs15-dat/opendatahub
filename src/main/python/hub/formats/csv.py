# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from osgeo import osr

import shapely
import fiona
import pandas as pd
import re
import pyproj
import logging

import csv
from hub.structures.file import File, FileGroup
from hub.formats import Format, Formatter, Parser, ParsingException
from hub.structures.frame import OdhType, OdhFrame, OdhSeries


logger = logging.getLogger(__name__)


class CSV(Format):
    label = 'CSV'

    description = """
    Ein Datensatz pro Zeile und die Spalten durch Kommas oder Semikolon getrennt.
    Die erste Zeile enthält die Namen der einzelnen Felder.
    """

    example = """
        Name,Vorname,Alter
        Scala,Fabio,24
        Hüsler,Christoph,27
        Liebi,Remo,26
    """

    extension = 'csv'

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == cls.extension


class CSVFormatter(Formatter):
    targets = CSV,

    FALLBACK_TYPE = 'String'

    TYPE_MAP = {
        OdhType.INTEGER: 'Integer',
        OdhType.SMALLINT: 'Integer',
        OdhType.BIGINT: 'Integer',
        OdhType.FLOAT: 'Real',
        OdhType.TEXT: 'String',
        OdhType.DATETIME: 'DateTime',
        OdhType.GEOMETRY: 'WKT',
        # boolean? interval?
    }

    @classmethod
    def _create_csvt(cls, df):
        # http://www.gdal.org/drv_csv.html
        # http://giswiki.hsr.ch/GeoCSV
        csvt_line = ';'.join('"{}"'.format(cls.TYPE_MAP.get(s.odh_type, cls.FALLBACK_TYPE)) for i, s in df.iteritems())
        return File.from_string(df.name + '.csvt', csvt_line)

    @classmethod
    def _create_csv(cls, df):
        return File.from_string(df.name + '.csv',
                                df.as_safe_serializable().to_csv(index=False, encoding='UTF-8', sep=str(';')))

    @classmethod
    def _create_prj(cls, df):
        try:
            geometry = next(s for c, s in df.iteritems() if s.odh_type == OdhType.GEOMETRY and s.crs)
            proj = pyproj.Proj(geometry.crs)
            srs = osr.SpatialReference()
            srs.ImportFromProj4(str(proj.srs))  # char * -> no unicode
            return File.from_string(df.name + '.prj', srs.ExportToPrettyWkt())
        except StopIteration:
            return None

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        file_groups = []

        for df in dfs:
            files = [cls._create_csv(df), cls._create_csvt(df)]
            prj = cls._create_prj(df)
            if prj:
                files.append(prj)

            file_groups.append(FileGroup(files))

        return file_groups


class CSVParser(Parser):
    accepts = CSV,

    CSVT_RE = re.compile('\s*(\w+)\s*\(.*\)\s*', re.IGNORECASE)

    @classmethod
    def _parse_prj(cls, fg):
        prjs = fg.get_by_extension('prj')
        if prjs:
            prj = prjs[0]
            srs = osr.SpatialReference()

            srs.ImportFromWkt([prj.ustream.read()])
            return fiona.crs.from_string(srs.ExportToProj4())

        return {}

    @classmethod
    def _parse_csvt(cls, fg):
        csvts = fg.get_by_extension('csvt')
        if csvts:
            csvt = csvts[0]
            fields = csvt.stream.readline().split(';')
            try:
                return [cls.CSVT_RE.match(f).group(1).lower() for f in fields]
            except (AttributeError, IndexError) as e:
                logger.warn('Could not parse CSVT file "%s": %s', csvt.stream.read(), e.message)

        return ()

    @classmethod
    def _parse_csv(cls, fg):
        csv_file = fg.get_by_extension('csv')[0]
        line = next(l for l in csv_file.stream if l.strip() != '')  # first non-empty line
        delimiter = csv.Sniffer().sniff(line).delimiter
        # sep=None works for auto-detection but falls-back to Python instead of C engine
        return OdhFrame.from_df(pd.read_csv(csv_file.stream, encoding='UTF-8', sep=delimiter))

    @classmethod
    def _parse_integer(cls, i, s, df, types):
        return OdhType.INTEGER.convert(s)

    @classmethod
    def _parse_string(cls, i, s, df, types):
        return OdhType.TEXT.convert(s)

    @classmethod
    def _parse_real(cls, i, s, df, types):
        return OdhType.FLOAT.convert(s)

    @classmethod
    def _parse_date(cls, i, s, df, types):
        return pd.to_datetime(s, infer_datetime_format=True)  # format='%Y-%m-%d'

    @classmethod
    def _parse_time(cls, i, s, df, types):
        return pd.to_datetime(s, infer_datetime_format=True)  # format='%H:%M:%S'

    @classmethod
    def _parse_datetime(cls, i, s, df, types):
        return pd.to_datetime(s, infer_datetime_format=True)  # format='%Y-%m-%d %H:%M:%S'

    @classmethod
    def _parse_wkt(cls, i, s, df, types):
        s = s.apply(shapely.wkt.loads, convert_dtype=False)
        s.crs = df.crs
        return s

    @classmethod
    def _parse_easting(cls, ix, s, df, types):
        if ix > 0 and types[ix - 1] != 'northing':
            iy = types[ix:].index('northing')
            return cls._parse_point(df, ix, iy)

    @classmethod
    def _parse_northing(cls, iy, s, df, types):
        if iy > 0 and types[iy - 1] != 'easting':
            ix = types[iy:].index('easting')
            return cls._parse_point(df, ix, iy)

    @classmethod
    def _parse_point(cls, df, ix, iy):
        s = OdhType.FLOAT.convert(df.iloc[:, [ix, iy]]).apply(shapely.geometry.Point, axis=1)
        s.crs = df.crs
        return s

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        fg = file.file_group

        crs = cls._parse_prj(fg)
        types = cls._parse_csvt(fg)
        df = cls._parse_csv(fg)
        df.crs = crs

        if types:
            assert len(df.columns) == len(types)

            series = []
            for i, (c, s) in enumerate(df.iteritems()):
                type_ = types[i]
                parse_method = getattr(cls, '_parse_' + type_, None)
                if not parse_method:
                    raise ParsingException('Unknown GeoCSV type "{}"'.format(type_))
                series.append(parse_method(i, s, df, types))

            df = OdhSeries.concat([s for s in series if s is not None], axis=1)

        return df

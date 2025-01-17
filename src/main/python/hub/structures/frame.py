# -*- coding: utf-8 -*-

"""
Custom extensions to Series/GeoSeries and DataFrame/GeoDataFrame from pandas/geopandas.
"""

from __future__ import unicode_literals
import datetime as dt
import collections

from types import NoneType
import pandas as pd
import geopandas as gp
import numpy as np
import shapely.geometry
import os
import shapely.speedups
from shapely.geometry.base import GEOMETRY_TYPES

from hub.exceptions import warn
from hub.odhql.exceptions import OdhQLExecutionException
from opendatahub.utils.plugins import RegistrationMixin

if shapely.speedups.available:
    shapely.speedups.enable()


class OdhType(RegistrationMixin):
    """ Base class for the supported data types. """
    dtypes = ()
    ptypes = ()
    name = ''

    by_name = {}
    by_dtype = collections.defaultdict(list)
    by_ptype = collections.defaultdict(list)

    _is_abstract = True

    @classmethod
    def register_child(cls, name, bases, own_dict):
        """ Implementation for RegistrationMixin """
        if not own_dict.get('_is_abstract'):
            instance = cls()

            instance.ptype = cls.ptypes[0]
            instance.dtype = cls.dtypes[0]
            instance.name = cls.name or name.upper()

            setattr(OdhType, instance.name, instance)
            instance.by_name[instance.name] = instance
            for dtype in instance.dtypes:
                OdhType.by_dtype[dtype].append(instance)

            for ptype in instance.ptypes:
                OdhType.by_ptype[ptype].append(instance)

    @classmethod
    def identify_value(cls, value):
        """ Tries to guess the data type of a single value.
        :param value: Value to examine.
        :return: Data type, if one was detected. Otherwise, None is returned.
        """
        type_ = type(value)
        if issubclass(type_, np.generic):
            return cls.by_dtype[type_]
        else:
            try:
                return cls.by_ptype[type_][0]
            except:
                pass

    @classmethod
    def identify_series(cls, s):
        """ Tries to guess the data type of a series.
        :param s: Series to examine.
        :return: Data type, if one was detected. If the series contained no not-None values, TEXT is returned.
        """
        by_dtype = cls.by_dtype[s.dtype.type]
        if len(by_dtype) == 1:
            return by_dtype[0]

        first = s.first_valid_index()
        if first is not None:
            value = s.iat[first]
            return cls.identify_value(value)
        else:
            return cls.TEXT

    def convert(self, series):
        """ Convert a series to a different data type.
        :param series: Series to convert.
        :return: Converted series.
        """
        return series._constructor(series.values.astype(self.dtypes[0]), index=series.index).__finalize__(series)

    def __repr__(self):
        return 'OdhType({})'.format(self.name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)


class IntegerType(OdhType):
    """ 32-bit integer type and base for other integer types. """
    name = 'INTEGER'
    dtypes = np.int32,
    ptypes = int,

    def convert(self, series):
        """ Converts the series to integer.
        :type series: hub.structures.frame.OdhSeries
        :return: Converted series.
        """
        return series._constructor(series.values.astype(np.float_).astype(self.dtypes[0]),
                                   index=series.index).__finalize__(series)


class BigIntType(IntegerType):
    """ 64-bit integer type. """
    name = 'BIGINT'
    dtypes = np.int64,
    ptypes = int,


class SmallIntType(IntegerType):
    """ 16-bit integer type. """
    name = 'SMALLINT'
    dtypes = np.int16,
    ptypes = int,


class FloatType(OdhType):
    """ 64-bit floating point type. """
    name = 'FLOAT'
    dtypes = np.float64,
    ptypes = float,


class DateTimeType(OdhType):
    """ Date/time type. """
    name = 'DATETIME'
    dtypes = np.datetime64,
    ptypes = pd.Timestamp,

    def convert(self, series):
        """ Converts the series to datetime. This interprets the series as unix epoch (seconds from
        1970-01-01T00:00:00), so this only works for integer/float types.
        :type series: hub.structures.frame.OdhSeries
        :return: converted series.
        """
        if series.odh_type.ptype not in (int, float):
            raise OdhQLExecutionException('Unable to convert from {} to {}'.format(str(series.odh_type), str(self)))
        return series._constructor(pd.to_datetime(series, unit='s'), index=series.index).__finalize__(series)


class IntervalType(OdhType):
    """ Date/time interval type. """
    name = 'INTERVAL'
    dtypes = pd.Timedelta,
    ptypes = dt.timedelta,


class BooleanType(OdhType):
    """ Boolean type. """
    name = 'BOOLEAN'
    dtypes = np.bool_,
    ptypes = bool,


class TextType(OdhType):
    """ Text type. This is also used for all-None series.. """
    name = 'TEXT'
    dtypes = np.object_,
    ptypes = unicode, str, NoneType

    def convert(self, series):
        """ Convert the series to text.
        :type series: hub.structures.frame.OdhSeries
        :return: Converted series.
        """
        try:
            return series._constructor(series.values.astype(unicode).astype(object), index=series.index).__finalize__(
                series)
        except:  # fallback, slower
            return series._constructor(series.astype(unicode).astype(object), index=series.index).__finalize__(series)


class GeometryType(OdhType):
    """ Geometry type. Supported are Point, LineString, Polygon, LinearRing and their Multi* versions. """
    name = 'GEOMETRY'
    dtypes = np.object_,
    ptypes = (
        shapely.geometry.Point, shapely.geometry.LineString, shapely.geometry.Polygon, shapely.geometry.LinearRing,
        shapely.geometry.MultiLineString, shapely.geometry.MultiPoint, shapely.geometry.MultiPolygon
    )


class OdhFrame(pd.DataFrame):
    """ Custom extensions for pandas' DataFrame. """
    _metadata = ['name']

    @classmethod
    def from_df(cls, df, name=None):
        """ Convert a DataFrame into a OdhFrame.
        :param df: Data frame to wrap.
        :param name: The data frame's name.
        :return: Newly created OdhFrame instance.
        """
        odf = cls(df, index=df.index).__finalize__(df)
        odf.name = name or getattr(df, 'name', None)
        return odf

    def rename(self, *args, **kwargs):
        """ Rename a data frame.
        :param args:
        :param kwargs:
        :return: Renamed data frame.
        """
        old = self.copy() if kwargs.get('inplace', False) else self
        df = super(OdhFrame, self).rename(*args, **kwargs)
        df = df or self
        return df.__finalize__(old, method='rename')

    def __finalize__(self, other, method=None, **kwargs):
        super(OdhFrame, self).__finalize__(other, method=method, **kwargs)
        if method == 'concat':
            other = other.objs[0]
        elif method == 'merge':
            other = other.left

        if method == 'rename':
            for c0, c1 in zip(self.columns, other.columns):
                self[c0].__finalize__(other[c1], method='rename')
        else:
            for c in self.columns:
                if c in other:
                    self[c].__finalize__(other[c])
        return self

    @property
    def has_geoms(self):
        """
        :return: True if this data frame contains geometry columns.
        """
        return OdhType.GEOMETRY in [s.odh_type for c, s in self.iteritems()]

    def to_gdf(self, supported_geoms=set(GEOMETRY_TYPES)):
        """
        Converts the OdhFrame into a geopandas.GeoDataFrame for exporting it via Fiona (to GeoJSON, Shapefile, ...)
        :param supported_geoms: Set of supported geometry types. Others are dropped.
        """
        supported_geom_types = set(supported_geoms)

        # if we have multiple geometry columns and none of them is called "geometry" we pick the first
        # the formatters require a single geometry column as most file formats only support one
        df = self.copy()
        df.__class__ = gp.GeoDataFrame
        geoseries = collections.OrderedDict([(c, s) for c, s in df.iteritems() if s.odh_type == OdhType.GEOMETRY])
        geometry = geoseries.get('geometry', geoseries.values()[0]).copy()
        if geometry.name != 'geometry':
            warn('Column "{}" containing geometry was renamed to "geometry".'.format(geometry.name))
            df.rename(columns={geometry.name: 'geometry'}, inplace=True)

        # remove additional geometry series, not supported
        other_geoms = set(geoseries.keys()) - {geometry.name}
        if other_geoms:
            warn('Multiple geometries not supported. Dropped column(s): {}.'.format(', '.join(other_geoms)))
            df.drop(other_geoms, axis=1, inplace=True)

        df.crs = geometry.crs

        geom_type = geometry.first_valid_entry.geom_type if geometry.first_valid_entry else 'Point'
        geometry = gp.GeoSeries(geometry, crs=geometry.crs)
        geometry.iloc[~np.in1d(geometry[~pd.isnull(geometry)].geom_type, list(supported_geom_types))] = None
        geometry.fillna(EmptyGeometryMarker(geom_type), inplace=True)

        geom_types = geometry.geom_type
        unique_geom_types = geom_types.unique()

        if len(unique_geom_types) > 1:
            common_type = os.path.commonprefix([gt[::-1] for gt in geom_types.unique()])[::-1]
            multi_type = 'Multi' + common_type
            mask = None
            if common_type in supported_geom_types and multi_type in supported_geom_types:
                constructor = getattr(shapely.geometry, 'Multi' + common_type)
                mask = geom_types == common_type
            elif shapely.geometry.GeometryCollection.__name__ in supported_geom_types:
                constructor = shapely.geometry.GeometryCollection
                mask = Ellipsis
            else:
                geometry[geometry.geom_type != geom_type] = EmptyGeometryMarker(geom_type)

            if mask is not None:
                geometry[mask] = geometry[mask].apply(lambda g: constructor([g]))

        df['geometry'] = geometry
        return df

    @property
    def _constructor(self):
        return OdhFrame

    @property
    def _constructor_sliced(self):
        return OdhSeries

    def __getstate__(self):
        d = dict(_data=super(OdhFrame, self).__getstate__())
        d.update({attr: getattr(self, attr, None) for attr in self._metadata})
        d['series_metadata'] = {c: s._get_metadata() for c, s in self.iteritems()}
        return d

    def __setstate__(self, state):
        super(OdhFrame, self).__setstate__(state.pop('_data', None))
        for attr in self._metadata:
            setattr(self, attr, state.get(attr, None))

        series_metadata = state.pop('series_metadata', None)
        for c, s in self.iteritems():
            meta = series_metadata.get(c, {})
            for attr in self._constructor_sliced._metadata:
                setattr(s, attr, meta.get(attr, None))

    def as_safe_serializable(self):
        """
        :return: DataFrame which contains only exportable data (no objects)
        """
        df = self.copy()
        for col in df.columns:
            df[col] = df[col].as_safe_serializable()

        return df


class OdhSeries(pd.Series):
    """ Custom extensions for pandas' Series. """
    _metadata = ['name', '_odh_type', 'crs']

    def __init__(self, data, *args, **kwargs):
        if isinstance(data, pd.Series):
            self.__finalize__(data)
        super(OdhSeries, self).__init__(data, *args, **kwargs)
        self._odh_type = None
        self._first_valid_entry = None
        if not getattr(self, 'crs', None):
            self.crs = kwargs.get('crs', {})

    @property
    def odh_type(self):
        if not self._odh_type:
            self._odh_type = OdhType.identify_series(self)
        return self._odh_type

    def __finalize__(self, other, method=None, **kwargs):
        name = self.name if method == 'rename' else other.name
        super(OdhSeries, self).__finalize__(other, method=method, **kwargs)
        self.name = name
        return self

    @property
    def _constructor(self):
        return OdhSeries

    def _get_metadata(self):
        return {attr: getattr(self, attr, None) for attr in self._metadata}

    def __getstate__(self):
        d = super(OdhSeries, self).__getstate__()
        d.update(self._get_metadata())
        return d

    def __setstate__(self, state):
        super(OdhSeries, self).__setstate__(state)
        for attr in self._metadata:
            setattr(self, attr, state.get(attr, None))

    @property
    def first_valid_entry(self):
        if self._first_valid_entry is None:
            ix = self.first_valid_index()
            if ix is not None:
                self._first_valid_entry = self.iat[ix]
        return self._first_valid_entry

    @classmethod
    def concat(cls, series, *args, **kwargs):
        df = OdhFrame(pd.concat(series, *args, **kwargs))
        for i, (name, s) in enumerate(df.iteritems()):
            s.__finalize__(series[i])
        return df

    def to_crs(self, crs):
        if not self.crs:
            raise OdhQLExecutionException('Missing SRID on source column')

        if sorted(self.crs.items()) == sorted(crs.items()):
            return self

        return self.geom_op('to_crs', crs)

    def geom_op(self, op, *args, **kwargs):
        assert self.odh_type == OdhType.GEOMETRY, 'Cannot execute geometry function on non-geometry column'
        s = self.copy()
        mask = ~pd.isnull(s)
        gs = gp.GeoSeries(s[mask], crs=self.crs)
        attr = getattr(gs, op)
        result = attr(*args, **kwargs) if callable(attr) else attr
        if isinstance(result, pd.Series):
            s[mask] = result
            s.crs = getattr(result, 'crs', self.crs)
            result = s
        elif isinstance(result, pd.DataFrame):
            result = result.reindex(self.index)

        return result

    def as_safe_serializable(self):
        s = self
        if s.odh_type is not OdhType.TEXT:
            s = OdhType.TEXT.convert(s)

        return s


class EmptyGeometryMarker(shapely.geometry.Point):
    """ Replacement for empty geometry values - certain file formats don't handle those well at all. """

    def __init__(self, geom_type='Point'):
        self.__geom_type = geom_type
        super(EmptyGeometryMarker, self).__init__()

    def geometryType(self):
        return self.__geom_type


def monkey_patch_geopandas():
    """ Fix None handling in geopandas/shapely. """
    import geopandas.geodataframe as geodataframe

    original_mapping = geodataframe.mapping

    # https://github.com/Toblerity/Shapely/issues/250
    def mapping(geometry, *a, **kw):
        if geometry.__class__ == EmptyGeometryMarker:
            return None
        return original_mapping(geometry, *a, **kw)

    geodataframe.mapping = mapping


monkey_patch_geopandas()

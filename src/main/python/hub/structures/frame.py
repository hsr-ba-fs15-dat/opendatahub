# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""

"""
import datetime as dt
import collections

import pandas as pd
import geopandas as gp
import numpy as np
import shapely.geometry

from hub.odhql.exceptions import OdhQLExecutionException

from opendatahub.utils.plugins import RegistrationMixin


class OdhType(RegistrationMixin):
    dtypes = ()
    ptypes = ()
    name = ''

    by_name = {}
    by_dtype = collections.defaultdict(list)
    by_ptype = collections.defaultdict(list)

    _is_abstract = True

    @classmethod
    def register_child(cls, name, bases, own_dict):
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
    name = 'INTEGER'
    dtypes = np.int32,
    ptypes = int,

    def convert(self, series):
        return series._constructor(series.values.astype(np.float_).astype(self.dtypes[0]),
                                   index=series.index).__finalize__(series)


class BigIntType(IntegerType):
    name = 'BIGINT'
    dtypes = np.int64,
    ptypes = int,


class SmallIntType(IntegerType):
    name = 'SMALLINT'
    dtypes = np.int16,
    ptypes = int,


class FloatType(OdhType):
    name = 'FLOAT'
    dtypes = np.float64,
    ptypes = float,


class DateTimeType(OdhType):
    name = 'DATETIME'
    dtypes = np.datetime64,
    ptypes = pd.Timestamp,

    def convert(self, series):
        if series.odh_type.ptype not in (int, float):
            raise OdhQLExecutionException('Unable to convert from {} to {}'.format(str(series.odh_type), str(self)))
        return series._constructor(pd.to_datetime(series, unit='s'), index=series.index).__finalize__(series)


class IntervalType(OdhType):
    name = 'INTERVAL'
    dtypes = pd.Timedelta,
    ptypes = dt.timedelta,


class BooleanType(OdhType):
    name = 'BOOLEAN'
    dtypes = np.bool_,
    ptypes = bool,


class TextType(OdhType):
    name = 'TEXT'
    dtypes = np.object_,
    ptypes = unicode, str

    def convert(self, series):
        try:
            return series._constructor(series.values.astype(unicode).astype(object), index=series.index).__finalize__(
                series)
        except:  # fallback, slower
            return series._constructor(series.astype(unicode).astype(object), index=series.index).__finalize__(series)


class GeometryType(OdhType):
    name = 'GEOMETRY'
    dtypes = np.object_,
    ptypes = (
        shapely.geometry.Point, shapely.geometry.LineString, shapely.geometry.Polygon, shapely.geometry.LinearRing,
        shapely.geometry.MultiLineString, shapely.geometry.MultiPoint, shapely.geometry.MultiPolygon
    )


class OdhFrame(pd.DataFrame):
    _metadata = ['name']

    @classmethod
    def from_df(cls, df, name=None):
        odf = cls(df, index=df.index).__finalize__(df)
        odf.name = name or getattr(df, 'name', None)
        return odf

    def rename(self, *args, **kwargs):
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
        return OdhType.GEOMETRY in [s.odh_type for c, s in self.iteritems()]

    def to_gdf(self):
        # if we have multiple geometry columns and none of them is called "geometry" we pick the first
        # the formatters require a single geometry column as most file formats only support one
        df = self.copy()
        df.__class__ = gp.GeoDataFrame
        geoseries = collections.OrderedDict([(c, s) for c, s in df.iteritems() if s.odh_type == OdhType.GEOMETRY])
        geometry = geoseries.get('geometry', geoseries.values()[0]).copy()
        df.rename(columns={geometry.name: 'geometry'}, inplace=True)

        # remove additional geometry series, not supported
        df.drop(set(geoseries.keys()) - {geometry.name}, axis=1, inplace=True)

        df.crs = geometry.crs
        geom_type = geometry.first_valid_entry.geom_type
        geometry = gp.GeoSeries(geometry, crs=geometry.crs).fillna(EmptyGeometryMarker(geom_type))
        df['geometry'] = geometry

        # putmask/fillna does not work as the shapely objects seem to be recognized as array for some reason
        # for i in np.where(df.geometry.isnull())[0]:
        # df.geometry.iat[i] = empty_geometry

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
    _metadata = ['name', '_odh_type', 'crs']

    def __init__(self, data, *args, **kwargs):
        if isinstance(data, pd.Series):
            self.__finalize__(data)
        super(OdhSeries, self).__init__(data, *args, **kwargs)
        self._odh_type = None
        self._first_valid_entry = None

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
        assert self.odh_type == OdhType.GEOMETRY, 'Cannot convert CRS of non-geometry column'
        return self._constructor(gp.GeoSeries.to_crs.__func__(self, crs), index=self.index).__finalize__(self)

    def as_safe_serializable(self):
        s = self
        if s.odh_type is not OdhType.TEXT:
            s = OdhType.TEXT.convert(s)

        return s


class EmptyGeometryMarker(shapely.geometry.Point):
    def __init__(self, geom_type='Point'):
        self.__geom_type = geom_type
        super(EmptyGeometryMarker, self).__init__()

    def geometryType(self):
        return self.__geom_type


def monkey_patch_geopandas():
    import geopandas.geodataframe as geodataframe

    original_mapping = geodataframe.mapping

    def mapping(geometry, *a, **kw):
        if geometry.__class__ == EmptyGeometryMarker:
            return None
        return original_mapping(geometry, *a, **kw)

    geodataframe.mapping = mapping


monkey_patch_geopandas()

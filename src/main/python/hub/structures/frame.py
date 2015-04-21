"""

"""

import datetime as dt
import collections

import pandas as pd
import geopandas as gp
import numpy as np
from shapely.geometry.base import BaseGeometry

import hub.utils.common as com


class OdhType(object):
    by_name = {}
    by_dtype = collections.defaultdict(list)
    by_ptype = collections.defaultdict(list)

    def __init__(self, name, dtypes, ptypes):
        self.name = name
        self.dtypes = com.ensure_tuple(dtypes)
        self.ptypes = com.ensure_tuple(ptypes)

        self.by_name[name] = self

        for dtype in self.dtypes:
            self.by_dtype[dtype].append(self)

        for ptype in self.ptypes:
            self.by_ptype[ptype].append(self)

    @classmethod
    def identify_series(cls, s):
        by_dtype = cls.by_dtype[s.dtype.type]
        if len(by_dtype) == 1:
            return by_dtype[0]

        first = s.first_valid_index()
        if first is not None:
            ptype = type(s.iat[first])
            if issubclass(ptype, BaseGeometry):
                return cls.GEOMETRY
            else:
                return cls.by_ptype[ptype][0]
        else:
            return cls.TEXT

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


for name, dtype, ptype in (
        ('INTEGER', np.int32, int),
        ('BIGINT', np.int64, int),
        ('SMALLINT', np.int16, int),
        ('FLOAT', np.float64, float),
        ('DATETIME', np.datetime64, dt.datetime),
        ('INTERVAL', np.timedelta64, dt.time),
        ('BOOLEAN', np.bool_, bool),
        ('TEXT', np.object_, [unicode, str]),
        ('GEOMETRY', np.object_, BaseGeometry),
):
    setattr(OdhType, name, OdhType(name, dtype, ptype))


class OdhFrame(pd.DataFrame):
    _metadata = ['name']

    @classmethod
    def from_df(cls, df, name):
        df.__class__ = cls
        df._metadata = cls._metadata
        df.name = name
        return df

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
        geometry.name = 'geometry'
        geometry.__class__ == gp.GeoSeries
        df.crs = geometry.crs
        return df

    @property
    def _constructor(self):
        return OdhFrame

    @property
    def _constructor_sliced(self):
        return OdhSeries

    def __getstate__(self):
        d = super(OdhFrame, self).__getstate__()
        d.update({attr: getattr(self, attr, None) for attr in self._metadata})
        return d

    def __setstate__(self, state):
        super(OdhFrame, self).__setstate__(state)
        for attr in self._metadata:
            setattr(self, state.get(attr, None))


class OdhSeries(pd.Series):
    _metadata = ['name', '_odh_type', 'crs']

    def __init__(self, data, *args, **kwargs):
        if isinstance(data, pd.Series):
            self.__finalize__(data)
        super(OdhSeries, self).__init__(data, *args, **kwargs)
        self._odh_type = None

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

    def __getstate__(self):
        d = super(OdhSeries, self).__getstate__()
        d.update({attr: getattr(self, attr, None) for attr in self._metadata})
        return d

    def __setstate__(self, state):
        super(OdhSeries, self).__setstate__(state)
        for attr in self._metadata:
            setattr(self, state.get(attr, None))

    @classmethod
    def concat(cls, series, *args, **kwargs):
        df = OdhFrame(pd.concat(series, *args, **kwargs))
        for i, (name, s) in enumerate(df.iteritems()):
            s.__finalize__(series[i])
        return df

    def to_crs(self, crs):
        assert self.odh_type == OdhType.GEOMETRY, 'Cannot convert CRS of non-geometry column'
        return self._constructor(gp.GeoSeries.to_crs.__func__(self, crs)).__finalize__(self)

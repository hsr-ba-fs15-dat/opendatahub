"""

"""

import datetime as dt

import pandas as pd
import geopandas as gp
from shapely.geometry.base import BaseGeometry
import numpy as np
import collections

import types


TYPE_MAP = {
    np.complex256: None,
    np.complex128: None,
    np.complex64: None,
    np.void: None,
    np.timedelta64: dt.timedelta,
    np.datetime64: dt.datetime,
    np.float128: float,
    np.float64: float,
    np.float32: float,
    np.float16: float,
    np.uint64: int,
    np.uint32: int,
    np.uint16: int,
    np.uint8: int,
    np.int64: int,
    np.int32: int,
    np.int16: int,
    np.int8: int,
    np.unicode_: unicode,
    np.string_: str,
    np.bool_: bool,
    np.object_: object
}


class DataFrameUtils(object):
    @staticmethod
    def make_serializable(df):
        """
        :return: DataFrame which contains only exportable data (no objects)
        """

        # todo: this check probably shouldn't be made here
        if isinstance(df, types.ListType):
            return map(DataFrameUtils.make_serializable, df)

        df = df.copy()
        df.__class__ = pd.DataFrame
        for col in df.columns:
            temp = df[col].dropna()
            if len(temp) and temp.dtype == object and not isinstance(temp.iat[0], unicode):
                try:
                    df[col] = df[col].astype(unicode)
                except:
                    pass

        return df

    @staticmethod
    def get_col_types(df):
        cols = collections.OrderedDict()
        for colname in df:
            col = df[colname]
            first = col.first_valid_index()
            if first:
                type_ = type(col.iat[first])

            else:
                if col.dtype.type != np.object_:
                    type_ = TYPE_MAP[col.dtype.type]
                else:
                    if colname == 'geometry' or isinstance(col, gp.GeoSeries):
                        type_ = BaseGeometry
                    else:
                        type_ = str
            cols[colname] = type_

        return cols

    @staticmethod
    def get_picklable(df):
        """ Returns tuple with containing dataframe and metadata. Use from_unpickled to restore.
        """
        get_meta = lambda o: {k: getattr(o, k, None) for k in o._metadata}
        return (df, get_meta(df), {str(col): get_meta(df[col]) for col in df})

    @staticmethod
    def from_unpickled(tup):
        """ Restores dataframe metadata form get_picklable result, which is usually lost when pickling.
        """
        df, meta, col_meta = tup

        def set_meta(obj, metadict):
            for attr, value in meta.iteritems():
                if not getattr(obj, attr, None):
                    setattr(obj, attr, value)

        set_meta(df, meta)
        for colname, meta in col_meta.iteritems():
            set_meta(df[colname], meta)

        return df

    @staticmethod
    def to_json_dict(df, start, count):
        from hub.odhql.interpreter import OdhQLInterpreter
        slice_ = DataFrameUtils.make_serializable(df.iloc[start:start + count].fillna('NULL'))
        return {
            'columns': slice_.columns.tolist(),
            'types': {c: OdhQLInterpreter._resolve_type(t) for c, t in DataFrameUtils.get_col_types(df).iteritems()},
            'data': slice_.to_dict(orient='records'),
            'count': df.shape[0]
        }

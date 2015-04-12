"""

"""

import datetime as dt

import pandas as pd
import geopandas as gp
from shapely.geometry.base import BaseGeometry
import numpy as np
import collections


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
        df = pd.DataFrame(df.copy(True))
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
    def preserve_meta(new, old):
        new.__class__ = old.__class__
        for attr in getattr(old, '_metadata', []):
            object.__setattr__(new, attr, getattr(old, attr, None))

        return new

    @staticmethod
    def preserve_series_meta(df_new, df_old):
        for c_new, c_old in zip(df_new.columns, df_old.columns):
            DataFrameUtils.preserve_meta(df_new[c_new], df_old[c_old])

        return df_new

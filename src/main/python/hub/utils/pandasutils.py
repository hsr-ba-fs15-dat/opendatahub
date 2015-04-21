"""

"""

import datetime as dt

import pandas as pd
import numpy as np
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
    def to_json_dict(df, start, count):
        slice_ = DataFrameUtils.make_serializable(df.iloc[start:start + count].fillna('NULL'))
        return {
            'name': df.name,
            'columns': slice_.columns.tolist(),
            'types': {c: s.odh_type.name for c, s in df.iteritems()},
            'data': slice_.to_dict(orient='records'),
            'count': df.shape[0]
        }

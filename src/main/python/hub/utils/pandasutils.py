"""

"""

import datetime as dt

import numpy as np


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
    def to_json_dict(df, id, start, count):
        slice_ = df.iloc[start:start + count].as_safe_serializable().fillna('NULL')
        return {
            'name': 'ODH{}_{}'.format(id, df.name) if id else '',
            'columns': slice_.columns.tolist(),
            'types': {c: s.odh_type.name for c, s in df.iteritems()},
            'data': slice_.to_dict(orient='records'),
            'count': df.shape[0]
        }

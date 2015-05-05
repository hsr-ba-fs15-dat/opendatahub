# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""

"""


class DataFrameUtils(object):
    @staticmethod
    def to_json_dict(df, id, start, count):
        slice_ = df.iloc[start:start + count].reset_index(drop=True).as_safe_serializable().fillna('NULL')
        return {
            'name': getattr(df, 'name', None),
            'unique_name': 'ODH{}_{}'.format(id, df.name) if id else None,
            'columns': slice_.columns.tolist(),
            'types': {c: s.odh_type.name for c, s in df.iteritems()},
            'data': slice_.to_dict(orient='records'),
            'count': len(df),
            'parent': id
        }

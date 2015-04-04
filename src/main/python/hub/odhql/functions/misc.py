"""
Misc. functions/utils
"""

import pandas as pd
import numpy as np

from hub.odhql.functions.core import VectorizedFunction, OdhQLExecutionException


class NVL(VectorizedFunction):
    name = 'NVL'

    def apply(self, a, b):
        return a.where(~pd.isnull(a), b)


class Cast(VectorizedFunction):
    name = 'CAST'

    type_map = {
        'str': str,
        'string': str,
        'varchar': str,
        'int': int,
        'integer': int,
        'smallint': int,
        'bigint': int,
        'float': float,
        'decimal': float,
        'numeric': float,
        'double': float,
        'double precision': float,
        'real': float,
        'null': None,
        'bool': np.bool_,
        'boolean': np.bool_,
    }

    def apply(self, values, dtypes):
        type_ = self.type_map.get(dtypes[0].lower())
        if not type_:
            raise OdhQLExecutionException('CAST: Type "{}" does not exist'.format(type_))
        return values.astype(type_)

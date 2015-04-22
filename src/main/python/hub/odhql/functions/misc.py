"""
Misc. functions/utils
"""

import pandas as pd

from hub.structures.frame import OdhType

from hub.odhql.exceptions import OdhQLExecutionException
from hub.odhql.functions.core import VectorizedFunction


class NVL(VectorizedFunction):
    name = 'NVL'

    def apply(self, a, b):
        return a.where(~pd.isnull(a), b)


class Round(VectorizedFunction):
    name = 'ROUND'

    def apply(self, col, decimals):
        self.assert_float('column', col)
        self.assert_int('decimals', decimals)
        self.assert_value()
        return self.expand(col).round(decimals)


class Cast(VectorizedFunction):
    name = 'CAST'

    def apply(self, values, type_):
        type_ = type_.upper()
        self.assert_in('type', type_.upper(), OdhType.by_name.keys())
        odh_type = OdhType.by_name[type_]
        try:
            return odh_type.convert(self.expand(values))
        except ValueError as e:
            raise OdhQLExecutionException('{}: {}'.format(self.name, e.message))

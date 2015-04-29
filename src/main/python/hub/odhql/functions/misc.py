# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Misc. functions/utils
"""

import pandas as pd

from hub.structures.frame import OdhType
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
    """
    Konvertiert den Datentyp einer Spalte oder eines einzelnen Wertes.

    Parameter
        - `values`: Spalte oder Wert der konvertiert werden soll.
        - `datatype`: Gültiger ODHQL Datentyp

    Beispiel
        .. code:: sql

            CAST(ODH42.age, 'INTEGER') AS age
    """
    name = 'CAST'

    def apply(self, values, datatype):
        datatype = datatype.upper()
        self.assert_in('type', datatype.upper(), OdhType.by_name.keys())
        odh_type = OdhType.by_name[datatype]
        with self.errorhandler('Unable to cast ({exception})'):
            return odh_type.convert(self.expand(values))


class ToDate(VectorizedFunction):
    name = 'TO_DATE'

    def apply(self, values, format=None):
        values = self.expand(values)
        self.assert_str(0, values)
        with self.errorhandler('Unable to parse datetimes ({exception})'):
            return pd.to_datetime(values, format=format, infer_datetime_format=True, coerce=True)

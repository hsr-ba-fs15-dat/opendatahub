# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Misc. functions/utils
"""

import pandas as pd

from hub.structures.frame import OdhType
from hub.odhql.functions.core import VectorizedFunction


class NVL(VectorizedFunction):
    """
    Gibt das zweite Argument zurück, falls das erste NULL ist.

    Parameter
        - `a`: Spalte oder Wert der auf NULL geprüft werden soll
        - `b`: Spalte oder Wert der als Ersatz verwendet werden soll

    Beispiel
        .. code:: sql

         NVL(ODH12.title, '') as title
    """
    name = 'NVL'

    def apply(self, a, b):
        return a.where(~pd.isnull(a), b)


class Round(VectorizedFunction):
    """
    Rundet auf die angegebene Anzahl Nachkommastellen.

    Parameter:
        - `col`: Spalte oder Wert der gerundet werden soll. Muss vom Datentyp FLOAT sein.
        - `decimals`: Anzahl Nachkommastellen, auf die gerundet werden soll.

    Beispiel:
        .. code:: sql

         ROUND(ODH20.fraction, 4) AS fraction
    """
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
    """
    Konvertiert ein Datum in TEXT-Form zu DATETIME.

    Parameter
        - `values`: Spalte oder Wert der konvertiert werden soll.
        - `format`: Format-Angabe. Siehe `Dokumentation <https://docs.python.org/2/library/time.html#time.strftime>`_.

    Beispiel
        .. code:: sql

            TO_DATE(ODH5.baubeginn, '%d%m%Y') as baubeginn
    """
    name = 'TO_DATE'

    def apply(self, values, format=None):
        values = self.expand(values)
        self.assert_str(0, values)
        with self.errorhandler('Unable to parse datetimes ({exception})'):
            return pd.to_datetime(values, format=format, infer_datetime_format=True, coerce=True)

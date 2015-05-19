# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Example CONCAT function used in ODHQL. Copy this file and use a valid Python module name (e.g. my_function.py).
Your function will then be automatically loaded and made available within the ODH Query Language Interpreter.
See hub.odhql.function package for more concrete implementation examples.
"""

from hub.odhql.functions.core import VectorizedFunction


class Concat(VectorizedFunction):
    """
    Konkateniert eine Liste von TEXT-Spalten oder Werten.

    Parameter
        - `args`: Liste von TEXT-Spalten oder -Werten

    Beispiel
        .. code:: sql

            CONCAT(ODH5.given_name, ' ', ODH5.surname) AS name
    """
    name = 'CONCAT'

    def apply(self, a, b, *args):
        args = [self.expand(arg) for arg in [a, b] + list(args)]
        for arg in args:
            self.assert_str('string', arg)
        return args[0].str.cat(args[1:])

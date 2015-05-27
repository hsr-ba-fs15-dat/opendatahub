# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Example function for ODHQL. Copy this file and use a valid Python module name (e.g. my_function.py).
Your function will then be automatically loaded and made available within the ODH Query Language Interpreter.
See hub.odhql.function package for more concrete implementation examples.
"""

from hub.odhql.functions.core import VectorizedFunction


class ExampleFunction(VectorizedFunction):
    # __doc__ is used to generate function documentation (formatted as reStructured Text)
    # By convention, function names and other keywords should be written in all-caps.
    """
    Beispiel-Funktion für ODHQL, welche prüft, ob ein Integer-Feld den Wert 42 enthält.

    Parameter
        - `values`: Integer-Spalte

    Beispiel
        .. code:: sql

            IS42(t.some_field) AS is42
    """
    name = 'IS42'

    def apply(self, values):
        self.assert_int(0, values)
        return values == 42

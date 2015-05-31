# -*- coding: utf-8 -*-
from __future__ import unicode_literals

""" Misc. utility functions. """

import types


def ensure_tuple(val):
    """
    Ensures that value is a tuple, converted to a tuple or wrapped in one.
    :type val: any
    :return: A tuple
    """
    return tuple(val) if isinstance(val, (types.ListType, types.TupleType)) else (val,)


def str2bool(v):
    """
    Converts the strings 'true' and 'false' to their (python) boolean counterparts and returns the input
    unchanged for other values.
    :param v: str.
    :return: True/False if the input was 'true'/'false', v otherwise.
    """
    if v.lower() in ('true', 'false'):
        return v.lower() in ('true',)
    return v

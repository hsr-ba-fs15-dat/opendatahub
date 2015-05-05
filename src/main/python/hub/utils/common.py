# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""

"""

import types


def ensure_tuple(val):
    return tuple(val) if isinstance(val, (types.ListType, types.TupleType)) else (val,)


def str2bool(v):
    if v.lower() in ('true', 'false'):
        return v.lower() in ('true', )
    return v

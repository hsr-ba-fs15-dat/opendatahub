"""

"""

import types


def ensure_tuple(val):
    return tuple(val) if isinstance(val, (types.ListType, types.TupleType)) else (val,)

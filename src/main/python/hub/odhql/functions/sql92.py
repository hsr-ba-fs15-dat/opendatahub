"""
ANSI SQL (SQL 92) Functions
"""

from hub.odhql.functions.core import VectorizedFunction, OdhQLExecutionException


class CastFunction(VectorizedFunction):
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
    }

    def apply(self, values, dtypes):
        type_ = self.type_map.get(dtypes[0].lower())
        if not type:
            raise OdhQLExecutionException('CAST: Type "{}" does not exist'.format(type_))
        return values.astype(type)


class ConcatFunction(VectorizedFunction):
    name = 'CONCAT'

    def apply(self, a, b, *args):
        return a.str.cat([b] + list(args))

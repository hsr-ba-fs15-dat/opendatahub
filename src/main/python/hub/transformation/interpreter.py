"""
"""
import pandas as pd
import numpy as np
import hub.transformation.config as ast
from opendatahub.utils.plugins import RegistrationMixin
import inspect


class OdhQLExecutionException(Exception):
    pass


class OdhQLFunction(RegistrationMixin):
    _is_abstract = True
    functions = {}

    name = ''

    def __init__(self, raw_args=None):
        self.raw_args = raw_args or []
        self.check_args()

    def check_args(self):
        argspec = inspect.getargspec(self.apply)
        expected_args = len(argspec.args) - 1
        given_args = len(self.raw_args)
        if not (argspec.keywords or argspec.varargs) and given_args != expected_args:
            raise OdhQLExecutionException(
                '{} takes exactly {} arguments, {} given'.format(self.name, expected_args, given_args))

    @classmethod
    def register_child(cls, name, bases, own_dict):
        if not own_dict.get('_is_abstract'):
            name = own_dict.get('name') or name
            cls.functions[name.lower()] = cls

    @staticmethod
    def execute(name, args):
        fn = OdhQLFunction.create(name, args)
        return fn.execute()

    @staticmethod
    def create(name, args):
        try:
            cls = OdhQLFunction.functions[name.lower()]
        except KeyError:
            raise OdhQLExecutionException('Function "{}" does not exist'.format(name))

        return cls(args)


class VectorizedFunction(OdhQLFunction):
    _is_abstract = True

    def execute(self):
        df = pd.DataFrame({str(i): series for i, series in enumerate(self.raw_args)})
        return self.apply(*[df[c] for c in df.columns])

    def apply(self, *args):
        raise NotImplementedError


class ElementFunction(OdhQLFunction):
    _is_abstract = True

    def execute(self):
        df = pd.DataFrame({str(i): series for i, series in enumerate(self.raw_args)})
        return df.apply(lambda s: self.apply(*s), axis=1)

    def apply(self, *args):
        raise NotImplementedError


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


class SampleElementFunction(ElementFunction):
    name = 'TEST'

    def apply(self, a, b):
        return a + b


class OdhQLInterpreter(object):
    def __init__(self, stmt, datasources):
        self.stmt = stmt
        self.datasources = datasources
        self.df = None

    def execute(self):
        try:
            return self.interpret()
        except KeyError as e:
            raise  # todo
            raise OdhQLExecutionException('{} does not exist'.format(e.message))

    def interpret(self):
        # load dataframes and prepare them (prefix) for querying
        self.load()

        # build one big/dataframe
        for ds in self.stmt.data_sources:
            self.df = self.interpret_data_source(ds)

        # filter selected rows
        if stmt.filter_definitions:
            mask = self.interpret_filter(stmt.filter_definitions)
            self.df = self.df[mask]

        # select requested fields from filtered dataframe
        cols = [self.interpret_field(self.df, f) for f in self.stmt.fields]
        df = self.df.__class__(cols).T

        return df

    def load(self):
        self.dfs = {ds.alias: datasources[ds.name].copy() for ds in self.stmt.data_sources}
        for alias, df in self.dfs.items():
            pfx = alias + '.'
            df.rename(columns={name: pfx + name for name in df.columns}, inplace=True)

    def interpret_data_source(self, ds):
        if isinstance(ds, ast.JoinedDataSource):
            cond = ds.condition
            left = self.dfs[cond.left.prefix]
            right = self.dfs[cond.right.prefix]
            lname = cond.left.prefix + '.' + cond.left.name
            rname = cond.right.prefix + '.' + cond.right.name
            df = left.merge(right, how='left', left_on=lname, right_on=rname)
            self.dfs[cond.left.prefix] = self.dfs[cond.right.prefix] = df
            return df

        elif isinstance(ds, ast.DataSource):
            return self.dfs[ds.alias]

        else:
            raise ValueError('Unexpected DataSource type "{}"'.format(type(ds)))

    def interpret_field(self, df, field):

        if isinstance(field, ast.Field):
            alias = getattr(field, 'alias', field.name)
            name = field.prefix + '.' + field.name
            series = df[name]

        elif isinstance(field, ast.Expression):
            alias = getattr(field, 'alias', None)
            value = '"{}"'.format(field.value) if isinstance(field.value, basestring) else field.value

            evaluated = pd.eval(value)
            if not isinstance(evaluated, pd.Series):
                evaluated = np.full(df.shape[0], evaluated,
                                    dtype=object if isinstance(evaluated, basestring) else type(evaluated))

            series = pd.Series(evaluated, name=alias)

        elif isinstance(field, ast.Function):
            alias = getattr(field, 'alias', None)
            args = [self.interpret_field(df, arg) for arg in field.args]
            series = OdhQLFunction.execute(field.name, args)

        else:
            raise ValueError('Unknown field type "{}"'.format(type(field)))

        series.name = alias
        return series.reset_index(drop=True)

    def interpret_filter(self, filter):
        if isinstance(filter, ast.FilterAlternative):
            mask = None
            for condition in filter.conditions:
                temp = self.interpret_filter(condition)
                mask = mask | temp if mask is not None else temp

        elif isinstance(filter, ast.FilterCombination):
            mask = np.ones(self.df.shape[0], dtype=bool)
            for condition in filter.conditions:
                mask &= self.interpret_filter(condition)

        elif isinstance(filter, ast.BinaryCondition):
            left = self.interpret_field(self.df, filter.left)
            right = self.interpret_field(self.df, filter.right)

            if filter.operator == ast.BinaryCondition.Operator.equals:
                mask = left == right
            elif filter.operator == ast.BinaryCondition.Operator.greater:
                mask = left > right
            elif filter.operator == ast.BinaryCondition.Operator.greater_or_equal:
                mask = left >= right
            elif filter.operator == ast.BinaryCondition.Operator.less:
                mask = left < right
            elif filter.operator == ast.BinaryCondition.Operator.less_or_equal:
                mask = left <= right
            else:
                raise ValueError('Unknown operator "{}"'.format(filter.operator))

            if filter.invert:
                mask = ~mask

        elif isinstance(filter, ast.InCondition):
            pass  # todo
        elif isinstance(filter, ast.IsNullCondition):
            pass  # todo

        return mask


if __name__ == '__main__':
    from hub.tests.testutils import TestBase
    from hub.structures.file import FileGroup

    odhql = """
        SELECT  a.Name as Name,
                TEST(4, 4) as ElementFunction,
                CONCAT(a.Baubereich, a.Baunummer) as ConcatFunction,
                CAST(a.Baunummer, 'int') AS CastFunction,
                a.Baubereich AS Bereich
          FROM a
        JOIN aa ON a.Baunummer = aa.Baunummer
        JOIN a AS aaa ON aa.Baunummer = aaa.Baunummer
        WHERE a.Name = 'Sihlquai' OR a.Name = 'Spatzenweg' AND a.Baunummer = 12024
     """

    a = FileGroup.from_files(TestBase.get_test_file_path('trobdb/tiefbaustelle.json')).to_df()

    datasources = {
        'a': a,
        'aa': a
    }

    p = ast.OdhQLParser()
    stmt = p.parse(odhql)
    field = stmt.fields[0]

    print OdhQLInterpreter(stmt, datasources).execute()

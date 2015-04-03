"""
"""
import pandas as pd
import numpy as np

import hub.odhql.parser as parser
import hub.odhql.functions as functions
from hub.odhql.exceptions import OdhQLExecutionException


class OdhQLInterpreter(object):
    def __init__(self, source_dfs):
        self.source_dfs = {alias.lower(): df for alias, df in source_dfs.iteritems()}

        self.df = None
        self.dfs = None

    def execute(self, query):
        if isinstance(query, basestring):
            query = parser.OdhQLParser().parse(query)

        try:
            return self.interpret(query)
        except KeyError as e:
            raise  # todo
            raise OdhQLExecutionException('{} does not exist'.format(e.message))

    def interpret(self, query):
        # load dataframes and prepare them (prefix) for querying
        self.load(query)

        # build one big/dataframe
        for ds in query.data_sources:
            self.df = self.interpret_data_source(ds)

        # filter selected rows
        if query.filter_definitions:
            mask = self.interpret_filter(query.filter_definitions)
            self.df = self.df[mask]

        # select requested fields from filtered dataframe
        if self.df.shape[0]:
            cols = [self.interpret_field(self.df, f) for f in query.fields]
            self.df = self.df.__class__(cols).T

        return self.df

    def load(self, query):
        self.dfs = {ds.alias: self.source_dfs[ds.name.lower()].copy() for ds in query.data_sources}
        for alias, df in self.dfs.items():
            df.rename(columns={name: self.make_name(alias, name) for name in df.columns}, inplace=True)

    @classmethod
    def make_name(cls, prefix, name):
        return '{}.{}'.format(prefix.lower(), name.lower())

    def interpret_data_source(self, ds):
        if isinstance(ds, parser.JoinedDataSource):
            cond = ds.condition
            left = self.dfs[cond.left.prefix]
            right = self.dfs[cond.right.prefix]
            name_left = self.make_name(cond.left.prefix, cond.left.name)
            name_right = self.make_name(cond.right.prefix, cond.right.name)
            df = left.merge(right, how='left', left_on=name_left, right_on=name_right)
            self.dfs[cond.left.prefix] = self.dfs[cond.right.prefix] = df
            return df

        elif isinstance(ds, parser.DataSource):
            return self.dfs[ds.alias]

        else:
            assert False, 'Unexpected DataSource type "{}"'.format(type(ds))

    def interpret_field(self, df, field):
        alias = getattr(field, 'alias', None)

        if isinstance(field, parser.Field):
            alias = alias or field.name
            name = self.make_name(field.prefix, field.name)
            series = df[name]

        elif isinstance(field, parser.Expression):
            value = field.value

            if not isinstance(value, pd.Series):
                value = np.full(df.shape[0], value, dtype=object if isinstance(value, basestring) else type(value))

            series = pd.Series(value, name=alias)

        elif isinstance(field, parser.Function):
            args = [self.interpret_field(df, arg) for arg in field.args]
            series = functions.execute(field.name, args)

        else:
            assert False, 'Unknown field type "{}"'.format(type(field))

        series.name = alias
        return series.reset_index(drop=True)

    def interpret_filter(self, filter):
        if isinstance(filter, parser.FilterAlternative):
            mask = np.logical_or.reduce([self.interpret_filter(c) for c in filter.conditions])

        elif isinstance(filter, parser.FilterCombination):
            mask = np.logical_and.reduce([self.interpret_filter(c) for c in filter.conditions])

        elif isinstance(filter, parser.BinaryCondition):
            left = self.interpret_field(self.df, filter.left)
            right = self.interpret_field(self.df, filter.right)

            if filter.operator == parser.BinaryCondition.Operator.equals:
                mask = left == right
            elif filter.operator == parser.BinaryCondition.Operator.not_equals:
                mask = left != right
            elif filter.operator == parser.BinaryCondition.Operator.greater:
                mask = left > right
            elif filter.operator == parser.BinaryCondition.Operator.greater_or_equal:
                mask = left >= right
            elif filter.operator == parser.BinaryCondition.Operator.less:
                mask = left < right
            elif filter.operator == parser.BinaryCondition.Operator.less_or_equal:
                mask = left <= right
            elif filter.operator == parser.BinaryCondition.Operator.like:
                mask = left.str.contains(str(right[0]))
            else:
                assert False, 'Unknown operator "{}"'.format(filter.operator)

        elif isinstance(filter, parser.InCondition):
            in_list = pd.DataFrame([self.interpret_field(self.df, el) for el in filter.in_list])
            left = self.interpret_field(self.df, filter.left)
            mask = np.logical_or.reduce(left == in_list)

        elif isinstance(filter, parser.IsNullCondition):
            left = self.interpret_field(self.df, filter.field)
            mask = pd.isnull(left)

        else:
            assert False, 'Unknown filter type "{}"'.format(type(filter))

        return ~mask if getattr(filter, 'invert', False) else mask

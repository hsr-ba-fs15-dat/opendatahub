"""
"""
from __future__ import unicode_literals
import collections
import itertools

import pandas as pd
import geopandas as gp
import numpy as np
import re

import hub.odhql.parser as parser
import hub.odhql.functions as functions
from hub.odhql.exceptions import OdhQLExecutionException


class OdhQLInterpreter(object):
    FILE_GROUP_RE = re.compile('ODH([1-9]\d?)', re.IGNORECASE)

    def __init__(self, source_dfs):
        self.source_dfs = {alias.lower(): df for alias, df in source_dfs.iteritems()}

        self.df = None
        self.dfs = None

    @classmethod
    def parse_sources(cls, query):
        if isinstance(query, basestring):
            query = parser.OdhQLParser().parse(query)

        data_sources = itertools.chain(*[q.data_sources for q in query.queries]) if isinstance(query, parser.Union) \
            else query.data_sources

        ids = {}
        for ds in data_sources:
            try:
                ids[ds.name] = int(cls.FILE_GROUP_RE.match(ds.name).group(1))
            except Exception:
                raise OdhQLExecutionException('Table "{}" is not a valid OpenDataHub source'.format(ds.name))

        return ids

    def execute(self, query):
        if isinstance(query, basestring):
            query = parser.OdhQLParser().parse(query)

        try:
            return self.interpret(query)
        except KeyError as e:
            raise  # todo
            raise OdhQLExecutionException('{} does not exist'.format(e.message))

    def interpret(self, query):

        if isinstance(query, parser.Union):
            self.df = self.interpret_union(query.queries)
        else:
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
                cls = self.df.__class__
                kw = {}

                cols = [self.interpret_field(self.df, f) for f in query.fields]

                geoseries = collections.OrderedDict(
                    [(series.name, series) for series in cols if isinstance(series, gp.GeoSeries)])
                if geoseries:
                    cls = gp.GeoDataFrame
                    geometry = geoseries.get('geometry', geoseries.values()[0])
                    geometry.name = 'geometry'
                    kw['crs'] = geometry.crs

                self.df = cls(cols, **kw).T
            else:
                self.df = pd.DataFrame(columns=[getattr(f, 'alias', f.name) for f in query.fields])

        return self.df

    def load(self, query):
        self.dfs = {ds.alias: self.source_dfs[ds.name.lower()].copy() for ds in query.data_sources}
        for alias, df in self.dfs.items():
            df.rename(columns={name: self.make_name(alias, name) for name in df.columns}, inplace=True)

    @classmethod
    def make_name(cls, prefix, name):
        return '{}.{}'.format(prefix.lower(), name.lower())

    def interpret_union(self, queries):
        if len({len(q.fields) for q in queries}) > 1:
            raise OdhQLExecutionException('The number of selected fields for each query must match exactly.')

        merged = None
        columns = []

        for df in (self.__class__(self.source_dfs).execute(query) for query in queries):
            if merged is None:
                merged = df
                columns = merged.columns.tolist()
                merged.rename(columns={col: str(i) for i, col in enumerate(df)}, inplace=True)
            else:
                df.rename(columns={col: str(i) for i, col in enumerate(df)}, inplace=True)
                merged = merged.append(df)

        merged.rename(columns={str(i): col for i, col in enumerate(columns)}, inplace=True)
        return merged

    def interpret_data_source(self, ds):
        if isinstance(ds, parser.JoinedDataSource):
            cond = ds.condition
            left = self.dfs[cond.left.prefix]
            right = self.dfs[cond.right.prefix]
            name_left = self.make_name(cond.left.prefix, cond.left.name)
            name_right = self.make_name(cond.right.prefix, cond.right.name)
            df = left.merge(right, how='left', left_on=[name_left], right_on=[name_right])
            self.dfs[cond.left.prefix] = self.dfs[cond.right.prefix] = df
            return df

        elif isinstance(ds, parser.DataSource):
            return self.dfs[ds.alias]

        else:
            assert False, 'Unexpected DataSource type "{}"'.format(type(ds))

    def interpret_field(self, df, field, expand=True):
        alias = getattr(field, 'alias', None)

        if isinstance(field, parser.Field):
            alias = alias or field.name
            name = self.make_name(field.prefix, field.name)
            series = df[name]

        elif isinstance(field, parser.Expression):
            value = field.value

            if not expand:
                return value

            if not isinstance(value, pd.Series):
                value = np.full(df.shape[0], value, dtype=object if isinstance(value, basestring) else type(value))

            series = pd.Series(value, name=alias)

        elif isinstance(field, parser.Function):
            args = [self.interpret_field(df, arg, expand=False) for arg in field.args]
            series = functions.execute(field.name, df.shape[0], args)

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

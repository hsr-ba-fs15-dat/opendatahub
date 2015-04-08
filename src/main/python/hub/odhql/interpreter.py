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
        return self.interpret(query)

    def interpret(self, query):
        is_union = isinstance(query, parser.Union)

        if is_union:
            if len(query.queries) == 1:
                setattr(query.queries[0], 'order', query.order)
                query.order = None

            df = self.interpret_union(query.queries)
            colnames = df.columns.tolist()

        else:
            # load dataframes and prepare them (prefix) for querying
            dfs = self.load(query)

            # build one big/dataframe
            df = self.interpret_data_sources(dfs, query.data_sources)

            # filter selected rows
            if query.filter_definitions:
                mask = self.interpret_filter(df, query.filter_definitions)
                df = df[mask]

            # select requested fields from filtered dataframe
            if df.shape[0]:
                cls = df.__class__
                kw = {}

                cols = [self.interpret_field(df, f) for f in query.fields]

                geoseries = collections.OrderedDict(
                    [(series.name, series) for series in cols if isinstance(series, gp.GeoSeries)])
                if geoseries:
                    cls = gp.GeoDataFrame
                    geometry = geoseries.get('geometry', geoseries.values()[0])
                    geometry.name = 'geometry'
                    kw['crs'] = geometry.crs

                colnames = [c.name for c in cols]
                addtl_colnames = set(df.columns.tolist()) - set(colnames)
                addtl_cols = [df[c].reset_index(drop=True) for c in addtl_colnames]
                df = cls(cols + addtl_cols, **kw).T

            else:
                colnames = [getattr(f, 'alias', f.name) for f in query.fields]
                df = pd.DataFrame(columns=colnames)

        if getattr(query, 'order', None):
            self.interpret_order(df, query.order, colnames)

        return df[colnames]

    def load(self, query):
        dfs = {ds.alias: self.source_dfs[ds.name.lower()].copy() for ds in query.data_sources}
        for alias, df in dfs.items():
            df.rename(columns={name: self.make_name(alias, name) for name in df.columns}, inplace=True)

        return dfs

    @classmethod
    def make_name(cls, prefix, name):
        return '{}.{}'.format(prefix.lower(), name.lower())

    def interpret_union(self, queries):
        if len({len(q.fields) for q in queries}) > 1:
            raise OdhQLExecutionException('The number of selected fields for each query must match exactly.')

        merged = None
        columns = []

        for df in (self.interpret(query) for query in queries):
            if merged is None:
                merged = df
                columns = merged.columns.tolist()
                merged.rename(columns={col: str(i) for i, col in enumerate(df)}, inplace=True)
            else:
                df.rename(columns={col: str(i) for i, col in enumerate(df)}, inplace=True)
                merged = merged.append(df)

        merged.rename(columns={str(i): col for i, col in enumerate(columns)}, inplace=True)
        return merged

    def interpret_data_sources(self, dfs, data_sources):
        for ds in data_sources:
            if isinstance(ds, parser.JoinedDataSource):
                cond = ds.condition
                left = dfs[cond.left.prefix]
                right = dfs[cond.right.prefix]
                name_left = self.make_name(cond.left.prefix, cond.left.name)
                name_right = self.make_name(cond.right.prefix, cond.right.name)
                df = left.merge(right, how='left', left_on=[name_left], right_on=[name_right])
                dfs[cond.left.prefix] = dfs[cond.right.prefix] = df

            elif isinstance(ds, parser.DataSource):
                df = dfs[ds.alias]

            else:
                assert False, 'Unexpected DataSource type "{}"'.format(type(ds))

        return df

    def interpret_field(self, df, field, expand=True):
        alias = getattr(field, 'alias', None)

        if isinstance(field, parser.Field):
            alias = alias or field.name
            name = self.make_name(field.prefix, field.name)
            try:
                series = df[name].copy()
            except KeyError:
                raise OdhQLExecutionException('Column "{}" does not exist'.format(name))

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

    def interpret_filter(self, df, filter):
        if isinstance(filter, parser.FilterAlternative):
            mask = np.logical_or.reduce([self.interpret_filter(df, c) for c in filter.conditions])

        elif isinstance(filter, parser.FilterCombination):
            mask = np.logical_and.reduce([self.interpret_filter(df, c) for c in filter.conditions])

        elif isinstance(filter, parser.BinaryCondition):
            left = self.interpret_field(df, filter.left)
            right = self.interpret_field(df, filter.right)

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
            in_list = pd.DataFrame([self.interpret_field(df, el) for el in filter.in_list])
            left = self.interpret_field(df, filter.left)
            mask = np.logical_or.reduce(left == in_list)

        elif isinstance(filter, parser.IsNullCondition):
            left = self.interpret_field(df, filter.field)
            mask = pd.isnull(left)

        else:
            assert False, 'Unknown filter type "{}"'.format(type(filter))

        return ~mask if getattr(filter, 'invert', False) else mask

    def interpret_order(self, df, orders, colnames):
        cols = []
        ascending = []
        for i, order in enumerate(orders):
            field = order.field

            if isinstance(field, parser.OrderByPosition):
                try:
                    cols.append(colnames[field.position - 1])
                except IndexError:
                    raise OdhQLExecutionException(
                        'ORDER BY: Column "{}" does not exist. The resulting table has '
                        '{} columns'
                        .format(field.position, len(colnames)))

            elif isinstance(field, parser.Field):
                cols.append(self.make_name(field.prefix, field.name))
            elif isinstance(field, parser.OrderByAlias):
                cols.append(field.alias)
            else:
                assert False, 'Unknown order by type "{}"'.format(type(field))

            assert order.direction in (parser.OrderBy.Direction.ascending, parser.OrderBy.Direction.descending)
            ascending.append(True if order.direction == parser.OrderBy.Direction.ascending else False)

        try:
            df.sort(cols, ascending=ascending, inplace=True)
        except KeyError as e:
            raise OdhQLExecutionException('ORDER BY: Column with the name "{}" does not exist'.format(e.message))

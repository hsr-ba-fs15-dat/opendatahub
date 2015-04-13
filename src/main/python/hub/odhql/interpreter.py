"""
"""
from __future__ import unicode_literals
import collections
import itertools
import datetime as dt

import pandas as pd
import geopandas as gp
import numpy as np
import re
from shapely.geometry.base import BaseGeometry

from hub.utils.pandasutils import DataFrameUtils
import hub.odhql.parser as parser
import hub.odhql.functions as functions
from hub.odhql.exceptions import OdhQLExecutionException


class OdhQLInterpreter(object):
    FILE_GROUP_RE = re.compile('ODH([1-9]\d?)', re.IGNORECASE)

    TYPE_MAP = {
        int: 'INTEGER',
        float: 'FLOAT',
        str: 'STRING',
        unicode: 'STRING',
        BaseGeometry: 'GEOMETRY',
        dt.datetime: 'DATETIME',
        dt.timedelta: 'INTERVAL',
        bool: 'BOOLEAN',
    }

    def __init__(self, source_dfs):
        self.source_dfs = {alias.lower(): df for alias, df in source_dfs.iteritems()}

    @classmethod
    def resolve_type(cls, type_):
        if isinstance(type_, BaseGeometry):
            type_ = BaseGeometry

        return cls.TYPE_MAP[type_]

    @classmethod
    def assert_crs(cls, series, name=None):
        if not getattr(series, 'crs', None):
            name = name or series.name
            raise OdhQLExecutionException('Unknown reference system for column "{}". '
                                          'Please use ST_SetSRID to specify the reference system.'
                                          .format(name))

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
                all_cols = cols + addtl_cols

                df = DataFrameUtils.preserve_meta(pd.concat(all_cols, axis=1, copy=False), df)
                df.__class__ = cls

                for attr, val in kw.iteritems():
                    setattr(df, attr, val)
                for i, c in enumerate(df):
                    DataFrameUtils.preserve_meta(df[c], all_cols[i])

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
        coltypes = {}
        columns = []

        for df in (self.interpret(query) for query in queries):
            if merged is None:
                merged = df
                columns = merged.columns.tolist()
                coltypes = DataFrameUtils.get_col_types(df).values()

                old = df.copy()
                merged.rename(columns={col: str(i) for i, col in enumerate(df)}, inplace=True)
                merged = DataFrameUtils.preserve_series_meta(merged, old)

            else:
                for i, (ct0, ct1) in enumerate(zip(coltypes, DataFrameUtils.get_col_types(df).values())):
                    ct0, ct1 = self.resolve_type(ct0), self.resolve_type(ct1)
                    if ct0 != ct1:
                        raise OdhQLExecutionException('UNION: Type mismatch for column {} ({}). '
                                                      'Expected "{}" got "{}" instead'
                                                      .format(i + 1, columns[i], ct0, ct1))

                old = df.copy()
                df.rename(columns={col: str(i) for i, col in enumerate(df)}, inplace=True)
                df = DataFrameUtils.preserve_series_meta(df, old)

                for i, (old, new) in enumerate(zip(columns, old.columns.tolist())):
                    colname = str(i)
                    s_new = df[str(colname)]
                    if isinstance(s_new, gp.GeoSeries):
                        s_old = merged[str(colname)]
                        self.assert_crs(s_old, old)
                        self.assert_crs(s_new, new)
                        df[str(colname)] = s_new.to_crs(merged.crs)

                merged = merged.append(df, ignore_index=True)

        old = merged.copy()
        merged.rename(columns={str(i): col for i, col in enumerate(columns)}, inplace=True)
        merged = DataFrameUtils.preserve_series_meta(merged, old)
        return merged

    def interpret_data_sources(self, dfs, data_sources):
        aliases_left = []
        df = None
        for ds in data_sources:
            if isinstance(ds, parser.JoinedDataSource):
                cond = ds.condition

                names_left = []
                names_right = []
                for c in cond.conditions if isinstance(cond, parser.JoinConditionList) else (cond,):
                    left, right = (c.left, c.right) if c.left.prefix in aliases_left else (c.right, c.left)
                    names_left.append(self.make_name(left.prefix, left.name))
                    names_right.append(self.make_name(right.prefix, right.name))

                df_right = dfs[right.prefix]
                df = df.merge(df_right, left_on=names_left, right_on=names_right, suffixes=('', 'r'), copy=False)
                aliases_left.append(right.prefix)

            elif isinstance(ds, parser.DataSource):
                df = dfs[ds.alias]
                aliases_left.append(ds.alias)

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

    def interpret_filter(self, df, filter_):
        if isinstance(filter_, parser.FilterAlternative):
            mask = np.logical_or.reduce([self.interpret_filter(df, c) for c in filter_.conditions])

        elif isinstance(filter_, parser.FilterCombination):
            mask = np.logical_and.reduce([self.interpret_filter(df, c) for c in filter_.conditions])

        elif isinstance(filter_, parser.BinaryCondition):
            left = self.interpret_field(df, filter_.left)
            right = self.interpret_field(df, filter_.right)

            if filter_.operator == parser.BinaryCondition.Operator.equals:
                mask = left == right
            elif filter_.operator == parser.BinaryCondition.Operator.not_equals:
                mask = left != right
            elif filter_.operator == parser.BinaryCondition.Operator.greater:
                mask = left > right
            elif filter_.operator == parser.BinaryCondition.Operator.greater_or_equal:
                mask = left >= right
            elif filter_.operator == parser.BinaryCondition.Operator.less:
                mask = left < right
            elif filter_.operator == parser.BinaryCondition.Operator.less_or_equal:
                mask = left <= right
            elif filter_.operator == parser.BinaryCondition.Operator.like:
                mask = left.str.contains(str(right[0]))
            elif filter_.operator == parser.BinaryCondition.Operator.not_like:
                mask = ~left.str.contains(str(right[0]))
            else:
                assert False, 'Unknown operator "{}"'.format(filter_.operator)

        elif isinstance(filter_, parser.InCondition):
            in_list = pd.concat([self.interpret_field(df, el) for el in filter_.in_list], axis=1, copy=False).T
            left = self.interpret_field(df, filter_.left)
            mask = np.logical_or.reduce(left == in_list)

        elif isinstance(filter_, parser.IsNullCondition):
            left = self.interpret_field(df, filter_.field)
            mask = pd.isnull(left)

        else:
            assert False, 'Unknown filter type "{}"'.format(type(filter_))

        return ~mask if getattr(filter_, 'invert', False) else mask

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

"""
Core OdhQL interpreter. Meant to be compact and fast. All extended functionality (i.e. functions) are implemented
separately.
"""

from __future__ import unicode_literals
import collections
import itertools

import pandas as pd
import numpy as np
import re

from hub.structures.frame import OdhType, OdhSeries, OdhFrame
import hub.odhql.parser as parser
import hub.odhql.functions as functions
from hub.odhql.exceptions import OdhQLExecutionException


class OdhQLInterpreter(object):

    FILE_GROUP_RE = re.compile('ODH([1-9]\d?)(_"?.+?"?)?', re.IGNORECASE)

    def __init__(self, source_dfs):
        """
        :param source_dfs: DataFrames required by the underlying OdhQL query.
        :type source_dfs: dict
        """
        self.source_dfs = {alias.lower(): df for alias, df in source_dfs.iteritems()}

    @classmethod
    def _assert_crs(cls, series, name=None):
        """
        Throws an OdhQLExecutionException if a GeoSeries is missing a coordinate reference system
        :param name: Optional name of the series for the exception. Uses the name of the series if omitted.
        """
        if not getattr(series, 'crs', None):
            name = name or series.name
            raise OdhQLExecutionException('Unknown reference system for column "{}". '
                                          'Please use ST_SetSRID to specify the reference system.'
                                          .format(name))

    @classmethod
    def _make_name(cls, prefix, name):
        return '{}.{}'.format(prefix.lower(), name.lower())

    @classmethod
    def _ensure_unique_fields(cls, query):
        """
        Renames SELECT fields so that they are unique by adding a number (starting from 2) for duplicates
        :param query: hub.odhql.parser.Query
        :rtype: None
        """
        seen = collections.defaultdict(int)
        for f in query.fields:
            n = seen[f.alias] = seen[f.alias] + 1
            f.alias = '{}{}'.format(f.alias, bool(n - 1) * str(n))

    @classmethod
    def parse_sources(cls, query):
        """
        Parses the data sources (tables) used in the query
        :param query:
        :return: The name and ids of the data sources
        :rtype: dict[name] -> id
        """
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

    # @profilehooks.profile(immediate=True)
    def execute(self, query):
        """
        Executes an OdhQL query
        :type query: str or parsed query object
        :return: Resulting DataFrame of the query
        :rtype: :py:class: OdhFrame
        """
        if isinstance(query, basestring):
            query = parser.OdhQLParser().parse(query)
        return self._interpret(query)

    def _interpret(self, query):
        """
        High-level interpretation control-flow
        :param query: :py:class: hub.parser.Union or py:class: hub.parser.Query
        :return: Resulting DataFrame
        :rtype: :py:class: OdhFrame
        """
        is_union = isinstance(query, parser.Union)

        if is_union:
            # top-level object produced by the parser is *always* a Union object even if it's a single query
            # if it's a "real" UNION we need to sort (ORDER) at the end, otherwise propagate Union.order to Query.order
            if len(query.queries) == 1:
                setattr(query.queries[0], 'order', query.order)
                query.order = None

            df = self._interpret_union(query.queries)
            colnames = df.columns.tolist()

        else:
            self._ensure_unique_fields(query)

            # prepare
            dfs = self._load(query)

            # build one big/joined dataframe (FROM, JOIN)
            df = self._interpret_data_sources(dfs, query.data_sources)

            # filter selected rows (WHERE)
            if query.filter_definitions:
                mask = self._interpret_filter(df, query.filter_definitions)
                df = df[mask]

            # select requested fields from filtered dataframe
            if df.shape[0]:
                cols = [self._interpret_field(df, f) for f in query.fields]
                colnames = [c.name for c in cols]
                addtl_colnames = set(df.columns.tolist()) - set(colnames)
                # add non-selected cols to dataframe as well to allow ORDER BY later
                addtl_cols = [df[c].reset_index(drop=True) for c in addtl_colnames]
                all_cols = cols + addtl_cols
                df = OdhSeries.concat(all_cols, axis=1, copy=False).__finalize__(df)

            else:
                colnames = [getattr(f, 'alias', f.name) for f in query.fields]
                df = OdhFrame(columns=colnames)

        if getattr(query, 'order', None):
            self._interpret_order(df, query.order, colnames)

        # final column selection
        return df[colnames]

    def _load(self, query):
        """
        Load dataframes and prepare them (prefix) for querying
        :type query: hub.odhql.parser.Query
        :return: Renamed/prepared dataframes
        :rtype: dict[alias] -> DataFrame
        """
        dfs = {ds.alias: self.source_dfs[ds.name.lower()].copy() for ds in query.data_sources}
        for alias, df in dfs.items():
            df.rename(columns={name: self._make_name(alias, name) for name in df.columns}, inplace=True)

        return dfs

    def _interpret_union(self, queries):
        """
        Process a :py:class: hub.odhql.parser.Union object
        :type queries: list of :py:class: hub.odhql.parser.Query
        :rtype: DataFrame
        """
        if len({len(q.fields) for q in queries}) > 1:
            raise OdhQLExecutionException('The number of selected fields for each query must match exactly.')

        merged = None
        coltypes = {}
        columns = []

        # 1. interpret the queries
        # 2. rename all columns to str(index) to have matching names
        # 3. Convert CRS if geometries present
        # 4. concatenate dataframes (append)
        for df in (self._interpret(query) for query in queries):
            if merged is None:
                merged = df
                columns = merged.columns.tolist()
                coltypes = [df[c].odh_type for c in df.columns]
                merged.rename(columns={col: str(i) for i, col in enumerate(df)}, inplace=True)
            else:
                for i, c in enumerate(df.columns):
                    type_left, type_right = coltypes[i], df[c].odh_type
                    if type_left != type_right:
                        raise OdhQLExecutionException('UNION: Type mismatch for column {} ({}). '
                                                      'Expected "{}" got "{}" instead'
                                                      .format(i + 1, columns[i], type_left.name, type_right.name))

                old = df.copy()
                df.rename(columns={col: str(i) for i, col in enumerate(df)}, inplace=True)

                for i, (old, new) in enumerate(zip(columns, old.columns.tolist())):
                    colname = str(i)
                    s_new = df[str(colname)]
                    if s_new.odh_type == OdhType.GEOMETRY:
                        s_old = merged[str(colname)]
                        self._assert_crs(s_old, old)
                        self._assert_crs(s_new, new)
                        df[str(colname)] = s_new.to_crs(s_old.crs)

                merged = merged.append(df, ignore_index=True)

        merged.rename(columns={str(i): col for i, col in enumerate(columns)}, inplace=True)
        return merged

    def _interpret_data_sources(self, dfs, data_sources):
        """
        Loads the necesessary dataframe(s) from the given source frames and performs joins if given multiple
        :param dfs: Prepared dataframes, result of self._load()
        :param data_sources: Ordered list of :py:class: hub.odhql.parser.DataSource
        :return: (Joined) DataFrame
        """
        aliases_left = []  # aliases (table prefixes) currently contained in `d`
        df = None  # make flake8/pylint happy
        for ds in data_sources:
            if isinstance(ds, parser.JoinedDataSource):
                cond = ds.condition

                names_left = []
                names_right = []
                for c in cond.conditions if isinstance(cond, parser.JoinConditionList) else (cond,):
                    left, right = (c.left, c.right) if c.left.prefix in aliases_left else (c.right, c.left)
                    names_left.append(self._make_name(left.prefix, left.name))
                    names_right.append(self._make_name(right.prefix, right.name))

                df_right = dfs[right.prefix]
                try:
                    df = df.merge(df_right, left_on=names_left, right_on=names_right, suffixes=('', 'r'), copy=False)
                except KeyError as e:
                    raise OdhQLExecutionException('JOIN: Column "{}" does not exist'.format(e.message))
                aliases_left.append(right.prefix)

            elif isinstance(ds, parser.DataSource):
                df = dfs[ds.alias]
                aliases_left.append(ds.alias)

            else:
                assert False, 'Unexpected DataSource type "{}"'.format(type(ds))

        return df

    def _interpret_field(self, df, field, expand=True):
        """
        Selects a field from the dataframe
        :type df: pandas.core.frame.DataFrame
        :type field: AliasedField or AliasedFunction or Function or Expression or Field
        :type expand: bool
        :return: Series or single value if expand=False
        """
        alias = getattr(field, 'alias', None)

        if isinstance(field, parser.Field):
            alias = alias or field.name
            name = self._make_name(field.prefix, field.name)
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

            series = OdhSeries(value, name=alias)

        elif isinstance(field, parser.Function):
            args = [self._interpret_field(df, arg, expand=False) for arg in field.args]
            series = functions.execute(field.name, len(df), args)

        else:
            assert False, 'Unknown field type "{}"'.format(type(field))

        series = OdhSeries(series.reset_index(drop=True), name=alias)
        return series

    def _interpret_filter(self, df, filter_):
        """
        Recursively interprets a filter condition and returns a mask matching the shape of a series
        :param filter_: Subclass of hub.odhql.parser.FilterListBase
        :return: numpy.ndarray(dtype=numpy.bool_)
        """
        if isinstance(filter_, parser.FilterAlternative):
            mask = np.logical_or.reduce([self._interpret_filter(df, c) for c in filter_.conditions])

        elif isinstance(filter_, parser.FilterCombination):
            mask = np.logical_and.reduce([self._interpret_filter(df, c) for c in filter_.conditions])

        elif isinstance(filter_, parser.BinaryCondition):
            left = self._interpret_field(df, filter_.left)
            right = self._interpret_field(df, filter_.right)

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
            in_list = pd.concat([self._interpret_field(df, el) for el in filter_.in_list], axis=1, copy=False).T
            left = self._interpret_field(df, filter_.left)
            mask = np.logical_or.reduce(left == in_list)

        elif isinstance(filter_, parser.IsNullCondition):
            left = self._interpret_field(df, filter_.field)
            mask = pd.isnull(left)

        else:
            assert False, 'Unknown filter type "{}"'.format(type(filter_))

        return ~mask if getattr(filter_, 'invert', False) else mask

    def _interpret_order(self, df, orders, colnames):
        """
        Sorts the dataframe (ORDER BY) *in place*
        :param df: DataFrame to sort
        :param orders: List of OrderByPosition or OrderByAlias or OrderBy
        :param colnames: Column names selected by the user. Required for order by bounds check since the DataFrame
                         also contains non-selected columns (specifically for sorting purposes actually)
        :return: Sorted DataFrame
        """
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
                cols.append(self._make_name(field.prefix, field.name))
            elif isinstance(field, parser.OrderByAlias):
                cols.append(field.alias)
            else:
                assert False, 'Unknown order by type "{}"'.format(type(field))

            assert order.direction in (parser.OrderBy.Direction.ascending, parser.OrderBy.Direction.descending)
            ascending.append(True if order.direction == parser.OrderBy.Direction.ascending else False)

        try:
            df.sort(cols, ascending=ascending, inplace=True)
            return df
        except KeyError as e:
            raise OdhQLExecutionException('ORDER BY: Column with the name "{}" does not exist'.format(e.message))

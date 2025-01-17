# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import types

from hub.tests.testutils import TestBase
import hub.odhql.parser as odhql


class TestParser(TestBase):
    def test_validate_grammar(self):

        grammar = odhql.OdhQLParser.build_grammar()

        import pyparsing

        self.assertIsInstance(grammar, pyparsing.ParserElement)
        grammar.validate()

    def test_simple_field_mapping(self):
        p = odhql.OdhQLParser()
        result = p.parse('select b.a, b."b", b.c as d from b')

        fields = (f for f in result.fields)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.Field)
        self.assertEqual('a', field.expression.name)
        self.assertEqual('a', field.alias)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.Field)
        self.assertEqual('b', field.expression.name)
        self.assertEqual('b', field.alias)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.Field)
        self.assertEqual('c', field.expression.name)
        self.assertEqual('d', field.alias)

    def test_expressions(self):
        p = odhql.OdhQLParser()
        result = p.parse('select \'te st\' as "bl ub", 3 as "integer", -3 as negative, 4.5 as float, null as "null", '
                         'true as "true", false as "false" from b')

        fields = (f for f in result.fields)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.LiteralExpression)
        self.assertEqual('te st', field.expression.value)
        self.assertEqual('bl ub', field.alias)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.LiteralExpression)
        self.assertIsInstance(field.expression.value, int)
        self.assertEqual(3, field.expression.value)
        self.assertEqual('integer', field.alias)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.LiteralExpression)
        self.assertIsInstance(field.expression.value, int)
        self.assertEqual(-3, field.expression.value)
        self.assertEqual('negative', field.alias)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.LiteralExpression)
        self.assertIsInstance(field.expression.value, float)
        self.assertEqual(4.5, field.expression.value)
        self.assertEqual('float', field.alias)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.LiteralExpression)
        self.assertIsNone(field.expression.value)
        self.assertEqual('null', field.alias)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.LiteralExpression)
        self.assertTrue(field.expression.value)
        self.assertEqual('true', field.alias)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.LiteralExpression)
        self.assertFalse(field.expression.value)
        self.assertEqual('false', field.alias)

        try:
            next(fields)
            self.fail('test doesn\'t check all fields')
        except StopIteration:
            pass

    def test_function_call(self):
        p = odhql.OdhQLParser()
        result = p.parse('select nullary() as first, unary_str(\'a\') as "second", unary_num(3.14) as third, '
                         'binary(\'one\', 2) as fourth, unary_field(test.one) as fifth from test')

        self.assertEqual(5, len(result.fields))

        fields = (f for f in result.fields)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.Function)
        func = field.expression
        self.assertEqual('nullary', func.name)
        self.assertEqual('first', field.alias)
        self.assertIsInstance(func.args, types.ListType)
        self.assertEqual(0, len(func.args))

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.Function)
        func = field.expression
        self.assertEqual('unary_str', func.name)
        self.assertEqual('second', field.alias)
        self.assertIsInstance(func.args, types.ListType)
        self.assertIsInstance(func.args[0], odhql.LiteralExpression)
        self.assertEqual('a', func.args[0].value)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.Function)
        func = field.expression
        self.assertEqual('unary_num', func.name)
        self.assertEqual('third', field.alias)
        self.assertIsInstance(func.args, types.ListType)
        self.assertIsInstance(func.args[0], odhql.LiteralExpression)
        self.assertEqual(3.14, func.args[0].value)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.Function)
        func = field.expression
        self.assertEqual('binary', func.name)
        self.assertEqual('fourth', field.alias)
        self.assertIsInstance(func.args, types.ListType)
        self.assertIsInstance(func.args[0], odhql.LiteralExpression)
        self.assertEqual('one', func.args[0].value)
        self.assertIsInstance(func.args[1], odhql.LiteralExpression)
        self.assertEqual(2, func.args[1].value)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.Function)
        func = field.expression
        self.assertEqual('unary_field', func.name)
        self.assertEqual('fifth', field.alias)
        self.assertIsInstance(func.args, types.ListType)
        self.assertIsInstance(func.args[0], odhql.Field)
        self.assertEqual('one', func.args[0].name)
        self.assertEqual('test', func.args[0].prefix)

    def test_nested_function_call(self):
        p = odhql.OdhQLParser()
        result = p.parse('select outer(inner(t.some_field)) as func from test as t')

        outer = result.fields[0]
        self.assertIsInstance(outer, odhql.AliasedExpression)
        self.assertEqual('outer', outer.expression.name)
        self.assertEqual('func', outer.alias)

        self.assertEqual(1, len(outer.expression.args))

        inner = outer.expression.args[0]
        self.assertIsInstance(inner, odhql.Function)
        self.assertEqual('inner', inner.name)

        self.assertEqual(1, len(inner.args))
        inner_arg = inner.args[0]
        self.assertIsInstance(inner_arg, odhql.Field)
        self.assertEqual('some_field', inner_arg.name)
        self.assertEqual('t', inner_arg.prefix)

    def test_datasource(self):
        p = odhql.OdhQLParser()
        result = p.parse('select t.a from test as t')

        datasource = result.data_sources[0]
        self.assertIsInstance(datasource, odhql.DataSource)
        self.assertEqual('test', datasource.name)
        self.assertEqual('t', datasource.alias)

    def test_joins(self):
        p = odhql.OdhQLParser()
        result = p.parse('select first_alias.stuff '
                         'from first_name as first_alias '
                         'join second_name on first_alias.first_field = second_name.first_field '
                         'join third_name as third_alias on (third_alias.first_field = first_alias.first_field) '
                         'join fourth_name on (fourth_name.first_field = first_alias.first_field '
                         'and fourth_name.second_field = second_name.second_field)')

        datasources = (d for d in result.data_sources)

        ds = next(datasources)
        self.assertIsInstance(ds, odhql.DataSource)
        self.assertEqual('first_name', ds.name)
        self.assertEqual('first_alias', ds.alias)

        ds = next(datasources)
        self.assertIsInstance(ds, odhql.JoinedDataSource)
        self.assertEqual('second_name', ds.name)
        self.assertEqual('second_name', ds.alias)

        self.assertIsInstance(ds.condition, odhql.JoinCondition)

        self.assertIsInstance(ds.condition.left, odhql.Field)
        self.assertEqual(ds.condition.left.prefix, 'first_alias')
        self.assertEqual(ds.condition.left.name, 'first_field')

        self.assertIsInstance(ds.condition.right, odhql.Field)
        self.assertEqual(ds.condition.right.prefix, 'second_name')
        self.assertEqual(ds.condition.right.name, 'first_field')

        ds = next(datasources)
        self.assertIsInstance(ds, odhql.JoinedDataSource)
        self.assertEqual('third_name', ds.name)
        self.assertEqual('third_alias', ds.alias)

        self.assertIsInstance(ds.condition, odhql.JoinConditionList)
        self.assertEqual(1, len(ds.condition))

        self.assertIsInstance(ds.condition[0], odhql.JoinCondition)

        self.assertIsInstance(ds.condition[0].left, odhql.Field)
        self.assertEqual(ds.condition[0].left.prefix, 'third_alias')
        self.assertEqual(ds.condition[0].left.name, 'first_field')

        self.assertIsInstance(ds.condition[0].right, odhql.Field)
        self.assertEqual(ds.condition[0].right.prefix, 'first_alias')
        self.assertEqual(ds.condition[0].right.name, 'first_field')

        ds = next(datasources)
        self.assertIsInstance(ds, odhql.JoinedDataSource)
        self.assertEqual('fourth_name', ds.name)
        self.assertEqual('fourth_name', ds.alias)

        self.assertIsInstance(ds.condition, odhql.JoinConditionList)
        self.assertEqual(2, len(ds.condition))

        self.assertIsInstance(ds.condition[0], odhql.JoinCondition)

        self.assertIsInstance(ds.condition[0].left, odhql.Field)
        self.assertEqual(ds.condition[0].left.prefix, 'fourth_name')
        self.assertEqual(ds.condition[0].left.name, 'first_field')

        self.assertIsInstance(ds.condition[0].right, odhql.Field)
        self.assertEqual(ds.condition[0].right.prefix, 'first_alias')
        self.assertEqual(ds.condition[0].right.name, 'first_field')

        self.assertIsInstance(ds.condition[1], odhql.JoinCondition)

        self.assertIsInstance(ds.condition[1].left, odhql.Field)
        self.assertEqual(ds.condition[1].left.prefix, 'fourth_name')
        self.assertEqual(ds.condition[1].left.name, 'second_field')

        self.assertIsInstance(ds.condition[1].right, odhql.Field)
        self.assertEqual(ds.condition[1].right.prefix, 'second_name')
        self.assertEqual(ds.condition[1].right.name, 'second_field')

    def test_single_equals(self):
        p = odhql.OdhQLParser()
        result = p.parse('select t.a from t where t.a = 1')

        alt = result.filter_definitions
        self.assertIsInstance(alt, odhql.FilterAlternative)
        self.assertEqual(1, len(alt))

        comb = alt[0]
        self.assertIsInstance(comb, odhql.FilterCombination)
        self.assertEqual(1, len(comb))

        equal = comb[0]
        self.assertIsInstance(equal, odhql.BinaryCondition)
        self.assertIsInstance(equal.left, odhql.Field)
        self.assertEqual('a', equal.left.name)
        self.assertEqual('t', equal.left.prefix)

        self.assertEqual(odhql.BinaryCondition.Operator.equals, equal.operator)

        self.assertIsInstance(equal.right, odhql.LiteralExpression)
        self.assertEqual(1, equal.right.value)

    def test_binary_condition_operators(self):
        p = odhql.OdhQLParser()
        result = p.parse('select t.a from t '
                         'where t.equals = 1 '
                         'and t.not_equals != 1 '
                         'and t.less < 1 '
                         'and t.less_or_equal <= 1 '
                         'and t.greater > 1 '
                         'and t.greater_or_equal >= 1 '
                         'and t."like" like \'test\''
                         'and t.not_like not like \'text\'')

        self.assertIsInstance(result.filter_definitions, odhql.FilterAlternative)
        self.assertIsInstance(result.filter_definitions[0], odhql.FilterCombination)

        self.assertEqual(len(odhql.BinaryCondition.Operator), len(result.filter_definitions[0]),
                         msg='Missing operator test')

        for cond in result.filter_definitions[0]:
            self.assertIsInstance(cond, odhql.BinaryCondition)

            self.assertIsInstance(cond.left, odhql.Field)
            self.assertIsInstance(cond.right, odhql.LiteralExpression)

            self.assertEqual(str(cond.operator), 'Operator.{}'.format(cond.left.name))

    def test_single_isnull(self):
        p = odhql.OdhQLParser()
        result = p.parse('select t.a from t where t.a is null')

        self.assertIsInstance(result.filter_definitions, odhql.FilterAlternative)
        self.assertIsInstance(result.filter_definitions[0], odhql.FilterCombination)

        condition = result.filter_definitions[0][0]  # see test_single_equals
        self.assertIsInstance(condition, odhql.IsNullCondition)
        self.assertIsInstance(condition.field, odhql.Field)
        self.assertEqual('a', condition.field.name)

    def test_or_filter(self):
        p = odhql.OdhQLParser()
        result = p.parse('select t.a from t where 1 = t.a or t.b = \'b\'')

        alt = result.filter_definitions
        self.assertIsInstance(alt, odhql.FilterAlternative)
        self.assertEqual(2, len(alt))

        combinations = (c for c in alt)

        comb = next(combinations)
        self.assertIsInstance(comb, odhql.FilterCombination)
        self.assertEqual(1, len(comb))

        equal = comb[0]
        self.assertIsInstance(equal, odhql.BinaryCondition)
        self.assertIsInstance(equal.left, odhql.LiteralExpression)
        self.assertIsInstance(equal.right, odhql.Field)

        self.assertEqual(1, equal.left.value)
        self.assertEqual('a', equal.right.name)
        self.assertEqual('t', equal.right.prefix)

        comb = next(combinations)
        self.assertIsInstance(comb, odhql.FilterCombination)
        self.assertEqual(1, len(comb))

        equal = comb[0]
        self.assertIsInstance(equal, odhql.BinaryCondition)
        self.assertIsInstance(equal.left, odhql.Field)
        self.assertIsInstance(equal.right, odhql.LiteralExpression)

        self.assertEqual('b', equal.left.name)
        self.assertEqual('t', equal.left.prefix)
        self.assertEqual('b', equal.right.value)

    def test_predicate(self):
        p = odhql.OdhQLParser()
        result = p.parse('select t.a from t where is_valid(t.blub)')

        self.assertIsInstance(result, odhql.Query)

        alt = result.filter_definitions
        comb = alt[0]

        condition = comb[0]

        self.assertIsInstance(condition, odhql.PredicateCondition)
        self.assertIsInstance(condition.predicate, odhql.Function)

        self.assertEqual(condition.predicate.name, 'is_valid')

    def test_case_expression(self):
        p = odhql.OdhQLParser()
        result = p.parse('select t.a, '
                         'case when t.a=1 then \'one\' when t.a=2 then \'two\' else \'other\' end as test '
                         'from t')

        self.assertIsInstance(result, odhql.Query)
        self.assertEqual(2, len(result.fields))

        fields = (f for f in result.fields)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)
        self.assertIsInstance(field.expression, odhql.Field)

        field = next(fields)
        self.assertIsInstance(field, odhql.AliasedExpression)

        expr = field.expression

        self.assertIsInstance(expr, odhql.CaseExpression)

        self.assertEqual(3, len(expr.rules))

        rules = (r for r in expr.rules)

        rule = next(rules)
        self.assertIsInstance(rule, odhql.CaseRule)
        self.assertIsInstance(rule.condition, odhql.BinaryCondition)
        self.assertIsInstance(rule.condition.left, odhql.Field)
        self.assertEqual('a', rule.condition.left.name)

        self.assertIsInstance(rule.expression, odhql.LiteralExpression)
        self.assertEqual('one', rule.expression.value)

        rule = next(rules)
        self.assertIsInstance(rule, odhql.CaseRule)

        rule = next(rules)
        self.assertIsInstance(rule, odhql.CaseRule)
        self.assertIsNone(rule.condition)
        self.assertIsInstance(rule.expression, odhql.LiteralExpression)
        self.assertEqual('other', rule.expression.value)

    def test_complex_filter(self):
        p = odhql.OdhQLParser()
        result = p.parse('select t.a from t where (1 = t.a or t.b = \'b\') and t.c is null')

        """
        This is about as ugly as conditions get. (I lied, they get worse due to more nesting).

        Expected structure (A = FilterAlternative (or), C = FilterCombination (and), B = BinaryCondition (=),
            I = IsNullCondition:

        A[                                          (1)
            C[                                      (2)
                A[                                  (3)
                    C[ B(1 = t.a) ],                (4)
                    C [ B[(t.b = 'b')]              (5)
                ],
                I(t.c is null)                      (6)
            ]
        ]
        """

        self.assertIsInstance(result.filter_definitions, odhql.FilterAlternative)  # 1
        self.assertEqual(1, len(result.filter_definitions))

        comb = result.filter_definitions[0]  # 2
        self.assertIsInstance(comb, odhql.FilterCombination)
        self.assertEqual(2, len(comb))

        alt = comb[0]  # 3
        self.assertIsInstance(alt, odhql.FilterAlternative)
        self.assertEqual(2, len(alt))

        self.assertIsInstance(alt[0], odhql.FilterCombination)  # 4
        self.assertEqual(1, len(alt[0]))
        self.assertIsInstance(alt[0][0], odhql.BinaryCondition)

        self.assertIsInstance(alt[1], odhql.FilterCombination)  # 5
        self.assertEqual(1, len(alt[1]))
        self.assertIsInstance(alt[1][0], odhql.BinaryCondition)

        self.assertIsInstance(comb[1], odhql.IsNullCondition)  # 6

    def test_order_by(self):
        p = odhql.OdhQLParser()

        result = p.parse('select a.a, a.b from a order by a.a, 2 desc, a')

        self.assertEqual(3, len(result.order))

        order = result.order[0]
        self.assertIsInstance(order, odhql.OrderBy)

        self.assertIsInstance(order.field, odhql.Field)
        self.assertEqual('a', order.field.name)
        self.assertEqual('a', order.field.prefix)
        self.assertEqual(odhql.OrderBy.Direction.ascending, order.direction)

        order = result.order[1]
        self.assertIsInstance(order.field, odhql.OrderByPosition)
        self.assertEqual(2, order.field.position)
        self.assertEqual(odhql.OrderBy.Direction.descending, order.direction)

        order = result.order[2]
        self.assertIsInstance(order.field, odhql.OrderByAlias)
        self.assertEqual('a', order.field.alias)
        self.assertEqual(odhql.OrderBy.Direction.ascending, order.direction)

    def test_union(self):
        p = odhql.OdhQLParser()

        result = p.parse('select a.a from a union select b.a from b order by b.b')

        self.assertIsInstance(result, odhql.Union)

        queries = (q for q in result.queries)

        query = next(queries)
        self.assertIsInstance(query, odhql.Query)
        self.assertEqual(1, len(query.fields))

        query = next(queries)
        self.assertIsInstance(query, odhql.Query)
        self.assertEqual(1, len(query.fields))

    def test_comments(self):
        p = odhql.OdhQLParser()

        result = p.parse('select \'--\' as singlequote, -- comment\n \'test\' as "--" -- another comment\n from test')

        self.assertIsInstance(result, odhql.Query)

        self.assertEqual(2, len(result.fields))

        self.assertEqual(result.fields[0].expression.value, '--')
        self.assertEqual(result.fields[0].alias, 'singlequote')

        self.assertEqual(result.fields[1].expression.value, 'test')
        self.assertEqual(result.fields[1].alias, '--')

    def test_join_types(self):
        p = odhql.OdhQLParser()

        types = odhql.JoinedDataSource.JoinType

        def assert_join_type(type, query):
            result = p.parse(query)
            self.assertIsInstance(result, odhql.Query)

            join_ds = result.data_sources[1]
            self.assertIsInstance(join_ds, odhql.JoinedDataSource)

            self.assertEqual(type, join_ds.join_type, msg=str(type))

        assert_join_type(types.inner, 'select a.a from a join b on a.x = b.x')
        assert_join_type(types.left, 'select a.a from a left join b on a.x = b.x')
        assert_join_type(types.right, 'select a.a from a right join b on a.x = b.x')
        assert_join_type(types.outer, 'select a.a from a full join b on a.x = b.x')

    def test_malformed_expressions(self):
        p = odhql.OdhQLParser()

        # res = p.parse('select 1 as a from test WHERE 7dcasxa33sx')

        expressions_to_test = [
            ('select 1 as \'A\' from test', 'single quotes are not valid for aliases'),
            ('select 1 from test', 'expressions need aliases'),
            ('select f() from test', 'function calls need aliases'),
            ('select f from test', 'prefixes are mandatory'),
            ('select 1 as a b from test', 'aliases containing spaces need double quotes'),
            ('asdfasdf', 'garbage input'),
            ('select 1', 'no data source'),
            ('select 1 as a from test1, test2', 'multiple data sources need to be defined using joins'),
            ('select func( as f from test', 'malformed function call'),
            ('select outer(inner() as f from test', 'malformed nested function call'),
            ('select 1 as a from test WHERE 7dcasxa33sx', 'trailing garbage'),
            ('select a.a from a order by a.a union select b.a from b order by b.b', 'order only at end of unions'),
            ('select a.a from a order by -1', 'negative order by position is invalid'),
            ('select a.a from a order by 0', 'zero as order by position is invalid'),
            ('select 1.-1 as a from a', 'invalid float'),
            ('select a.a from a inner join b on a.x = b.x', 'just use \'join\' instead'),
            ('select a.a from a left outer join b on a.x = b.x', 'use \'left join\' instead'),
            ('select a.a from a right outer join b on a.x = b.x', 'use \'right join\' instead'),
            ('select a.a from a full outer  join b on a.x = b.x', 'use \'full join\' instead')
        ]

        for expr, reason in expressions_to_test:
            try:
                p.parse(expr)
                self.fail(reason)
            except AssertionError:
                raise
            except:
                pass

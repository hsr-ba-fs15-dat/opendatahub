import types

from hub.tests.testutils import TestBase
import hub.transformation.config as oql


class TestParser(TestBase):
    def test_simple_field_mapping(self):
        p = oql.OQLParser()
        result = p.parse('select b.a, b."b", b.c as d from b')

        fields = (f for f in result.fields)

        field = next(fields)
        self.assertIsInstance(field, oql.AliasedField)
        self.assertEqual('a', field.name)
        self.assertEqual('a', field.alias)

        field = next(fields)
        self.assertIsInstance(field, oql.AliasedField)
        self.assertEqual('b', field.name)
        self.assertEqual('b', field.alias)

        field = next(fields)
        self.assertIsInstance(field, oql.AliasedField)
        self.assertEqual('c', field.name)
        self.assertEqual('d', field.alias)

    def test_expressions(self):
        p = oql.OQLParser()
        result = p.parse('select \'te st\' as "bl ub", 3 as "integer", 4.5 as float from b')

        fields = (f for f in result.fields)

        field = next(fields)
        self.assertIsInstance(field, oql.AliasedExpression)
        self.assertEqual('te st', field.value)
        self.assertEqual('bl ub', field.alias)

        field = next(fields)
        self.assertIsInstance(field, oql.AliasedExpression)
        self.assertIsInstance(field.value, int)
        self.assertEqual(3, field.value)
        self.assertEqual('integer', field.alias)

        field = next(fields)
        self.assertIsInstance(field, oql.AliasedExpression)
        self.assertIsInstance(field.value, float)
        self.assertEqual(4.5, field.value)
        self.assertEqual('float', field.alias)

    def test_function_call(self):
        p = oql.OQLParser()
        result = p.parse('select nullary() as first, unary_str(\'a\') as "second", unary_num(3.14) as third, '
                         'binary(\'one\', 2) as fourth, unary_field(test.one) as fifth from test')

        self.assertEqual(5, len(result.fields))

        fields = (f for f in result.fields)

        field = next(fields)
        self.assertIsInstance(field, oql.AliasedFunction)
        self.assertEqual('nullary', field.name)
        self.assertEqual('first', field.alias)
        self.assertIsInstance(field.args, types.ListType)
        self.assertEqual(0, len(field.args))

        field = next(fields)
        self.assertIsInstance(field, oql.AliasedFunction)
        self.assertEqual('unary_str', field.name)
        self.assertEqual('second', field.alias)
        self.assertIsInstance(field.args, types.ListType)
        self.assertIsInstance(field.args[0], oql.Expression)
        self.assertEqual('a', field.args[0].value)

        field = next(fields)
        self.assertIsInstance(field, oql.AliasedFunction)
        self.assertEqual('unary_num', field.name)
        self.assertEqual('third', field.alias)
        self.assertIsInstance(field.args, types.ListType)
        self.assertIsInstance(field.args[0], oql.Expression)
        self.assertEqual(3.14, field.args[0].value)

        field = next(fields)
        self.assertIsInstance(field, oql.AliasedFunction)
        self.assertEqual('binary', field.name)
        self.assertEqual('fourth', field.alias)
        self.assertIsInstance(field.args, types.ListType)
        self.assertIsInstance(field.args[0], oql.Expression)
        self.assertEqual('one', field.args[0].value)
        self.assertIsInstance(field.args[1], oql.Expression)
        self.assertEqual(2, field.args[1].value)

        field = next(fields)
        self.assertIsInstance(field, oql.AliasedFunction)
        self.assertEqual('unary_field', field.name)
        self.assertEqual('fifth', field.alias)
        self.assertIsInstance(field.args, types.ListType)
        self.assertIsInstance(field.args[0], oql.Field)
        self.assertEqual('one', field.args[0].name)
        self.assertEqual('test', field.args[0].prefix)

    def test_nested_function_call(self):
        p = oql.OQLParser()
        result = p.parse('select outer(inner(t.some_field)) as func from test as t')

        outer = result.fields[0]
        self.assertIsInstance(outer, oql.AliasedFunction)
        self.assertEqual('outer', outer.name)
        self.assertEqual('func', outer.alias)

        self.assertEqual(1, len(outer.args))

        inner = outer.args[0]
        self.assertIsInstance(inner, oql.Function)
        self.assertEqual('inner', inner.name)

        self.assertEqual(1, len(inner.args))
        inner_arg = inner.args[0]
        self.assertIsInstance(inner_arg, oql.Field)
        self.assertEqual('some_field', inner_arg.name)
        self.assertEqual('t', inner_arg.prefix)

    def test_datasource(self):
        p = oql.OQLParser()
        result = p.parse('select t.a from test as t')

        datasource = result.datasources[0]
        self.assertIsInstance(datasource, oql.DataSource)
        self.assertEqual('test', datasource.name)
        self.assertEqual('t', datasource.alias)

    def test_joins(self):
        p = oql.OQLParser()
        result = p.parse('select first_alias.stuff '
                         'from first_name as first_alias '
                         'join second_name on first_alias.first_field = second_name.first_field '
                         'join third_name as third_alias on (third_alias.first_field = first_alias.first_field) '
                         'join fourth_name on (fourth_name.first_field = first_alias.first_field '
                         'and fourth_name.second_field = second_name.second_field)')

        datasources = (d for d in result.datasources)

        ds = next(datasources)
        self.assertIsInstance(ds, oql.DataSource)
        self.assertEqual('first_name', ds.name)
        self.assertEqual('first_alias', ds.alias)

        ds = next(datasources)
        self.assertIsInstance(ds, oql.JoinedDataSource)
        self.assertEqual('second_name', ds.name)
        self.assertEqual('second_name', ds.alias)

        self.assertIsInstance(ds.condition, oql.JoinCondition)

        self.assertIsInstance(ds.condition.left, oql.Field)
        self.assertEqual(ds.condition.left.prefix, 'first_alias')
        self.assertEqual(ds.condition.left.name, 'first_field')

        self.assertIsInstance(ds.condition.right, oql.Field)
        self.assertEqual(ds.condition.right.prefix, 'second_name')
        self.assertEqual(ds.condition.right.name, 'first_field')

        ds = next(datasources)
        self.assertIsInstance(ds, oql.JoinedDataSource)
        self.assertEqual('third_name', ds.name)
        self.assertEqual('third_alias', ds.alias)

        self.assertIsInstance(ds.condition, oql.JoinConditionList)
        self.assertEqual(1, len(ds.condition))

        self.assertIsInstance(ds.condition[0], oql.JoinCondition)

        self.assertIsInstance(ds.condition[0].left, oql.Field)
        self.assertEqual(ds.condition[0].left.prefix, 'third_alias')
        self.assertEqual(ds.condition[0].left.name, 'first_field')

        self.assertIsInstance(ds.condition[0].right, oql.Field)
        self.assertEqual(ds.condition[0].right.prefix, 'first_alias')
        self.assertEqual(ds.condition[0].right.name, 'first_field')

        ds = next(datasources)
        self.assertIsInstance(ds, oql.JoinedDataSource)
        self.assertEqual('fourth_name', ds.name)
        self.assertEqual('fourth_name', ds.alias)

        self.assertIsInstance(ds.condition, oql.JoinConditionList)
        self.assertEqual(2, len(ds.condition))

        self.assertIsInstance(ds.condition[0], oql.JoinCondition)

        self.assertIsInstance(ds.condition[0].left, oql.Field)
        self.assertEqual(ds.condition[0].left.prefix, 'fourth_name')
        self.assertEqual(ds.condition[0].left.name, 'first_field')

        self.assertIsInstance(ds.condition[0].right, oql.Field)
        self.assertEqual(ds.condition[0].right.prefix, 'first_alias')
        self.assertEqual(ds.condition[0].right.name, 'first_field')

        self.assertIsInstance(ds.condition[1], oql.JoinCondition)

        self.assertIsInstance(ds.condition[1].left, oql.Field)
        self.assertEqual(ds.condition[1].left.prefix, 'fourth_name')
        self.assertEqual(ds.condition[1].left.name, 'second_field')

        self.assertIsInstance(ds.condition[1].right, oql.Field)
        self.assertEqual(ds.condition[1].right.prefix, 'second_name')
        self.assertEqual(ds.condition[1].right.name, 'second_field')

    def test_malformed_expressions(self):
        p = oql.OQLParser()

        expressions_to_test = [
            ('select 1 as \'A\' from test', 'single quotes are not valid for aliases'),
            ('select 1 from test', 'expressions need aliases'),
            ('asdfasdf', 'garbage input'),
            ('select 1', 'no data source'),
            ('select 1 as a from test1, test2', 'multiple data sources need to be defined using joins')
        ]

        for expr, reason in expressions_to_test:
            try:
                p.parse(expr)
                self.fail(reason)
            except:
                pass

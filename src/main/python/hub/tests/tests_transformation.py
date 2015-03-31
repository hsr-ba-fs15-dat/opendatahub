import types

from hub.tests.testutils import TestBase
import hub.transformation.config as oql


class TestParser(TestBase):
    def test_simple_field_mapping(self):
        p = oql.OQLParser()
        result = p.parse('select a, "b", c as d from b')

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

        self.assertDictContainsSubset({'name': 'b'}, result.datasources[0])

    def test_function_call(self):
        p = oql.OQLParser()
        result = p.parse('select nullary() as first, unary_str(\'a\') as "second", unary_num(3.14) as third, '
                         'binary(\'one\', 2) as fourth from test')

        self.assertEqual(4, len(result.fields))

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

    def test_datasource(self):
        p = oql.OQLParser()
        result = p.parse('select a from test as t')

        datasource = result.datasources[0]
        self.assertIsInstance(datasource, oql.DataSource)
        self.assertEqual('test', datasource.name)
        self.assertEqual('t', datasource.alias)

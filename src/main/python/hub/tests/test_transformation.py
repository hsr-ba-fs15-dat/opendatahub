from hub.tests.testutils import TestBase
import hub.transformation.config


class TestParser(TestBase):
    def test_simple_field_mapping(self):
        p = hub.transformation.config.OQLParser()
        result = p.parse('select a, b, "te st" as "bl ub", 3 as "number" from b')

        self.assertDictContainsSubset({'name': 'a'}, result.fields[0])
        self.assertDictContainsSubset({'name': 'b'}, result.fields[1])
        self.assertDictContainsSubset({'name': 'te st', 'alias': 'bl ub'}, result.fields[2])
        self.assertDictContainsSubset({'value': '3', 'alias': 'number'}, result.fields[3])

        self.assertDictContainsSubset({'name': 'b'}, result.datasources[0])

import json
import types
from . import testutils

from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile


class RestApiTests(testutils.TestBase):
    def setUp(self):
        f = open(self.get_test_file_path('test-addresses.csv'), 'r')
        self.data = {
            'name': 'REST Api test',
            'description': 'post_document test',
            'file': SimpleUploadedFile(f.name, f.read())
        }

        self.client = APIClient()

        self.response = self.client.post('/api/v1/documents', self.data)
        self.response_json = json.loads(self.response.content)

    def test_post(self):
        """ Verifies that setUp managed to create a document via the api.
        """
        self.assertEqual(200, self.response.status_code)

        self.assertIn('name', self.response_json)
        self.assertEqual(self.data['name'], self.response_json['name'])

        self.assertIn('description', self.response_json)
        self.assertEqual(self.data['description'], self.response_json['description'])

    def test_get_document(self):
        """ AssertionError: Path must be within the project
        """
        self.assertIn('id', self.response_json)

        document_id = self.response_json['id']
        result = self.client.get('/api/v1/documents/%d' % document_id)

        result_json = json.loads(result.content)

        self.assertIn('id', result_json)
        self.assertEqual(document_id, result_json['id'])
        self.assertIn('name', result_json)
        self.assertEqual(self.data['name'], result_json['name'])
        self.assertIn('description', result_json)
        self.assertEqual(self.data['description'], result_json['description'])

    def assert_record_ok(self, record):
        self.assertIn('id', record)
        self.assertIn('url', record)
        self.assertIn('content', record)

    def test_get_document_records(self):
        """ Retrieves the records for a certain document and verifies the result.
        """
        self.assertIn('id', self.response_json)

        document_id = self.response_json['id']
        result = self.client.get('/api/v1/documents/%d/records' % document_id)

        result_json = json.loads(result.content)

        self.assertIn('results', result_json)
        self.assertIsInstance(result_json['results'], types.ListType)
        self.assertEqual(2, len(result_json['results']))

        for record in result_json['results']:
            self.assert_record_ok(record)

    def test_get_records(self):
        """ Retrieves a list of known records and verifies the result.
        """
        result = self.client.get('/api/v1/records')

        result_json = json.loads(result.content)

        self.assertIn('results', result_json)
        self.assertIsInstance(result_json['results'], types.ListType)
        self.assertGreater(len(result_json['results']), 2)

        for record in result_json['results']:
            self.assert_record_ok(record)

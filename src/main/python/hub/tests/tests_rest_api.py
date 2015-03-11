from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import types
import testutils


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
        self.assertEqual(200, self.response.status_code)

        self.assertIn('name', self.response_json)
        self.assertEqual(self.data['name'], self.response_json['name'])

        self.assertIn('description', self.response_json)
        self.assertEqual(self.data['description'], self.response_json['description'])

    def test_get_document(self):
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

    def test_get_document_records(self):
        self.assertIn('id', self.response_json)

        document_id = self.response_json['id']
        result = self.client.get('/api/v1/documents/%d/records' % document_id)

        result_json = json.loads(result.content)

        self.assertIsInstance(result_json, types.ListType)
        self.assertEqual(2, len(result_json))

        for record in result_json:
            self.assertIn('id', record)
            self.assertIn('url', record)
            self.assertIn('content', record)

    def test_get_records(self):
        result = self.client.get('/api/v1/records')

        result_json = json.loads(result.content)

        self.assertIsInstance(result_json, types.ListType)
        self.assertGreater(len(result_json), 2)

        for record in result_json:
            self.assertIn('id', record)
            self.assertIn('url', record)
            self.assertIn('content', record)


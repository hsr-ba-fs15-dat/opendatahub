import json

from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from . import testutils


class RestApiTests(testutils.TestBase):
    def setUp(self):
        f = open(self.get_test_file_path('test-addresses.csv'), 'r')
        self.data = {
            'name': 'REST Api test',
            'description': 'post_document test',
            'file': SimpleUploadedFile(f.name, f.read())
        }

        self.client = APIClient()

        self.response = self.client.post('/api/v1/document', self.data)
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
        result = self.client.get('/api/v1/document/%d' % document_id)

        result_json = json.loads(result.content)

        self.assertIn('id', result_json)
        self.assertEqual(document_id, result_json['id'])
        self.assertIn('name', result_json)
        self.assertEqual(self.data['name'], result_json['name'])
        self.assertIn('description', result_json)
        self.assertEqual(self.data['description'], result_json['description'])

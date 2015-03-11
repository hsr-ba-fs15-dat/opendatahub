from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
import json

import testutils


class RestApiTests(testutils.TestBase):
    def test_post(self):
        f = open(self.get_test_file_path('test-addresses.csv'), 'r')

        client = APIClient()
        data = {
            'name': 'REST Api test',
            'description': 'post_document test',
            'file': SimpleUploadedFile(f.name, f.read())
        }

        response = client.post('/api/v1/documents', data)
        self.assertEqual(200, response.status_code)
        body = json.loads(response.content)

        self.assertTrue('name' in body)
        self.assertEqual(data['name'], body['name'])

        self.assertTrue('description' in body)
        self.assertEqual(data['description'], body['description'])

    def runTest(self):
        self.test_post()

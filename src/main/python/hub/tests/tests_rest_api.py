import json

from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from . import testutils


class RestApiTests(testutils.TestBase):

    def setUp(self):
        self.user = self.get_test_user()

        with open(self.get_test_file_path('test-addresses.csv'), 'r') as f:
            self.data = {
                'name': 'REST Api test',
                'description': 'post_document test',
                'file': SimpleUploadedFile(f.name, f.read())
            }

    def get_client(self, authenticate=True):
        client = APIClient()
        if authenticate:
            client.login(username=self.username, password=self.password)
        return client

    def do_post(self, client):
        self.response = client.post('/api/v1/document/', self.data)
        self.response_json = json.loads(self.response.content)

    def test_post(self):
        """ Verifies that setUp managed to create a document via the api.
        """
        self.do_post(self.get_client())

        self.assertEqual(200, self.response.status_code)

        self.assertIn('name', self.response_json)
        self.assertEqual(self.data['name'], self.response_json['name'])

        self.assertIn('description', self.response_json)
        self.assertEqual(self.data['description'], self.response_json['description'])

    def test_post_requires_auth(self):
        try:
            self.do_post(self.get_client(authenticate=False))
            self.fail('creating a document is supposed to require authentication')
        except:
            pass

    def test_get_document(self):
        """ AssertionError: Path must be within the project
        """
        self.do_post(self.get_client())

        self.assertIn('id', self.response_json)

        document_id = self.response_json['id']
        result = self.get_client(authenticate=False).get('/api/v1/document/%d/' % document_id)

        result_json = json.loads(result.content)

        self.assertIn('id', result_json)
        self.assertEqual(document_id, result_json['id'])
        self.assertIn('name', result_json)
        self.assertEqual(self.data['name'], result_json['name'])
        self.assertIn('description', result_json)
        self.assertEqual(self.data['description'], result_json['description'])

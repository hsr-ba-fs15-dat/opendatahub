# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.test import APITestCase

from hub.management.commands.loadfixtures import Command as LoadFixtures


class FixtureTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.format_list = [fmt['name'] for fmt in client.get('/api/v1/format/').data]

        LoadFixtures(parse=False).handle()

EXCLUDED_DOCUMENTS = [
    'Dummy',  # those are for paging tests and just repeat
    'employee'  # excessive amounts of data, actually segfaults for interlis1
]


def find_fixtures(client):
    documents = client.get('/api/v1/document/?count=50&page=1')
    transformations = client.get('/api/v1/transformation/?count=50&page=1')
    fixtures = []

    for doc in documents.data['results']:
        if all(doc['name'].find(excluded) < 0 for excluded in EXCLUDED_DOCUMENTS):
            file_groups = client.get(doc['file_groups'])
            for fg in file_groups.data:
                fixtures.append(('ODH{}'.format(fg['id']), fg['data']))

    for trf in transformations.data['results']:
        fixtures.append(('TRF{}'.format(trf['id']), '/api/v1/transformation/{}/data/'.format(trf['id'])))

    return fixtures


def get_fixture_test(id, url):
    def fixture_test(self):
        for fmt in self.format_list:
            data_url = '{}?fmt={}'.format(url, fmt)
            try:
                response = self.client.get(data_url)
                print '{} -> {}'.format(data_url, response.status_code)

                self.assertEqual(200, response.status_code)
            except Exception as e:
                self.fail('Format {} failed with error {}'.format(fmt, e.message))

    return fixture_test


from rest_framework.test import APIClient

LoadFixtures(parse=False).handle()

client = APIClient()
fixtures = find_fixtures(client)
for (id, url) in fixtures:
    test = get_fixture_test(id, url)
    test_name = 'test_{}'.format(id.lower())

    setattr(FixtureTest, test_name, test)
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.test import APITestCase

'''
This test tries to format all fixtures with all available formats.
'''


class FixtureTest(APITestCase):
    pass


EXCLUDED_DOCUMENTS = [
    'Dummy',  # those are for paging tests and just repeat
    'employee',  # excessive amounts of data, actually segfaults for interlis1
    'children'  # same
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


def get_fixture_test(id, url, fmt):
    def fixture_test(self):
        data_url = '{}?fmt={}'.format(url, fmt)
        response = self.client.get(data_url)

        self.assertEqual(200, response.status_code)

    return fixture_test


from rest_framework.test import APIClient

print 'Creating test cases...'
client = APIClient()
fixtures = find_fixtures(client)
format_list = [fmt['name'].lower() for fmt in client.get('/api/v1/format/').data]

if 'geopackage' in format_list:  # GDAL >= 2.0.0 - support in 1.11.x is basically unusable
    format_list.remove('geopackage')
# if 'interlis1' in format_list:  # GDAL < 1.11.0 - results in segfault from 1.11.0 onwards (not fixed in 2.0.0beta1)
#    format_list.remove('interlis1')

for (id, url) in fixtures:
    for fmt in format_list:
        test = get_fixture_test(id, url, fmt)
        test_name = 'test_{}_{}'.format(id.lower(), fmt.lower())

        setattr(FixtureTest, test_name, test)
print 'Preparations done.'

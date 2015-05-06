# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.test import APITestCase

from hub.management.commands.loadfixtures import Command as LoadFixtures


class FixtureTest(APITestCase):
    EXCLUDED_DOCUMENTS = [
        'Dummy',  # those are for paging tests and just repeat
        'employee'  # excessive amounts of data, actually segfaults for interlis1
    ]

    @classmethod
    def setUpClass(cls):
        LoadFixtures().handle()

    def setUp(self):
        self.format_list = [fmt['name'] for fmt in self.client.get('/api/v1/format/').data]

        self.fixtures = self.find_fixtures()

    def find_fixtures(self):
        documents = self.client.get('/api/v1/document/?count=50&page=1')
        transformations = self.client.get('/api/v1/transformation/?count=50&page=1')
        fixtures = []

        for doc in documents.data['results']:
            if all(doc['name'].find(excluded) < 0 for excluded in self.EXCLUDED_DOCUMENTS):
                file_groups = self.client.get(doc['file_groups'])
                for fg in file_groups.data:
                    fixtures.append(('ODH{}'.format(fg['id']), fg['data']))

        for trf in transformations.data['results']:
            fixtures.append(('TRF{}'.format(trf['id']), '/api/v1/transformation/{}/data/'.format(trf['id'])))

        return fixtures

    def test_formats(self):
        results = {}
        for (id, url) in self.fixtures:
            results[id] = {}
            for fmt in self.format_list:
                data_url = '{}?fmt={}'.format(url, fmt)
                try:
                    response = self.client.get(data_url)
                    print '{} -> {}'.format(data_url, response.status_code)

                    results[id][fmt] = response.status_code
                except Exception as e:
                    print '{} -> {}'.format(data_url, e.message)
                    results[id][fmt] = e

        for id, fmts in results.iteritems():
            for fmt, status in fmts.iteritems():
                print "id: {}, fmt: {} -> {}".format(id, fmt, status)

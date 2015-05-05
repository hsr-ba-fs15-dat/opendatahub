# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Tests for data formats
"""

from hub.tests.testutils import TestBase
from hub import formats
from hub.structures.file import FileGroup


class FormatsTests(TestBase):
    TESTS = {
        # first element in considered the main file
        ('mockaroo.com.csv',): formats.CSV,
        ('mockaroo.com.json',): formats.JSON,
        ('mockaroo.com.xlsx',): formats.Excel,
        ('gml/Bahnhoefe.gml', 'gml/Bahnhoefe.gfs', 'gml/Bahnhoefe.xsd',): formats.GML,
        ('json/Bahnhoefe.json',): formats.GeoJSON,
        ('kml/Bahnhoefe.kml',): formats.KML,
        ('shp/Bahnhoefe.shp', 'shp/Bahnhoefe.shx', 'shp/Bahnhoefe.dbf', 'shp/Bahnhoefe.ili'): formats.Shapefile,
    }

    def test_identification(self):
        for files, format in self.TESTS.iteritems():
            fg = FileGroup.from_files(*[TestBase.get_test_file_path(f) for f in files])
            self.assertIs(formats.identify(fg[0]), format)

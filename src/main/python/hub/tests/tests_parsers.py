"""
Tests for parsers
"""

from pandas import DataFrame

from geopandas import GeoDataFrame

from hub.tests.testutils import TestBase
from hub.structures.file import FileGroup


class FormatsTests(TestBase):
    TESTS = {
        # first element in considered the main file
        ('mockaroo.com.csv',): DataFrame,
        ('mockaroo.com.json',): DataFrame,
        ('mockaroo.com.xlsx',): DataFrame,
        ('mockaroo.com.xml',): DataFrame,
        ('gml/Bahnhoefe.gml', 'gml/Bahnhoefe.gfs', 'gml/Bahnhoefe.xsd',): GeoDataFrame,
        ('json/Bahnhoefe.json',): GeoDataFrame,
        ('kml/Bahnhoefe.kml',): GeoDataFrame,
        ('shp/Bahnhoefe.shp', 'shp/Bahnhoefe.shx', 'shp/Bahnhoefe.dbf', 'shp/Bahnhoefe.ili'): GeoDataFrame,
    }

    def test_parse(self):
        for files, format in self.TESTS.iteritems():
            fg = FileGroup.from_files(*[TestBase.get_test_file_path(f) for f in files])
            for r in fg[0].to_df():
                self.assertIsInstance(r, format)

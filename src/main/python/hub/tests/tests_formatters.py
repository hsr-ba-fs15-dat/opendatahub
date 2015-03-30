"""
Tests for formatters
"""

from hub.tests.testutils import TestBase
from hub.structures.file import FileGroup
from hub.formats import Format


class FormatsTests(TestBase):
    TO_FORMATS = set(Format.formats.values())

    TESTS = {
        # first element in considered the main file
        ('mockaroo.com.csv',): TO_FORMATS,
        ('mockaroo.com.json',): TO_FORMATS,
        ('mockaroo.com.xlsx',): TO_FORMATS,
        ('gml/Bahnhoefe.gml', 'gml/Bahnhoefe.gfs', 'gml/Bahnhoefe.xsd',): TO_FORMATS,
        ('json/Bahnhoefe.json',): TO_FORMATS,
        ('kml/Bahnhoefe.kml',): TO_FORMATS,
        ('shp/Bahnhoefe.shp', 'shp/Bahnhoefe.shx', 'shp/Bahnhoefe.dbf', 'shp/Bahnhoefe.ili'): TO_FORMATS,
    }

    def test_format(self):
        for files, formats in self.TESTS.iteritems():
            fg = FileGroup.from_files(*[TestBase.get_test_file_path(f) for f in files])
            for format in formats:
                result = fg[0].to_format(format)
                self.assertIsInstance(result, FileGroup)

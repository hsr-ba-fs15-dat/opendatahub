"""

"""

from hub.tests.testutils import TestBase
from hub.utils.ogr2ogr import ogr2ogr, OGR_BY_EXTENSION
from hub.structures.file import FileGroup


class Ogr2OgrUtilsTests(TestBase):
    def test_gml_to_all(self):
        file_group = FileGroup.from_files(
            self.get_test_file_path('gml/Bahnhoefe.gml'),
            self.get_test_file_path('gml/Bahnhoefe.gfs'),
            self.get_test_file_path('gml/Bahnhoefe.xsd'),
        )

        for ext, ogr_format in OGR_BY_EXTENSION.iteritems():
            new_file_group = ogr2ogr(file_group, ogr_format)
            self.assertIn('Bahnhoefe.' + ext, new_file_group.names)

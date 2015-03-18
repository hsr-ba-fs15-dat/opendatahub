"""

"""

from hub.tests.testutils import TestBase
from cStringIO import StringIO
from hub.utils.ogr2ogr import ogr2ogr, OGR2OGR_FILES
import os


class Ogr2OgrUtilsTests(TestBase):

    def get_files(self, *file_paths):
        from_files = {}

        for file_path in file_paths:
            abs_path = self.get_test_file_path(file_path)
            with open(abs_path) as f:
                from_files[os.path.basename(abs_path)] = StringIO(''.join(f.readlines()))

        return from_files

    def test_gml_to_all(self):
        from_files = self.get_files('gml/Bahnhoefe.gml', 'gml/Bahnhoefe.gfs', 'gml/Bahnhoefe.xsd')
        for ext, ogr_type in OGR2OGR_FILES.iteritems():
            to_files = ogr2ogr(from_files, ogr_type)
            assert ext in [os.path.splitext(name)[1] for name in to_files.keys()]

"""
Tests for ogr2ogr wrapper/utility
"""

from hub.tests.testutils import TestBase
from hub.utils.ogr2ogr import ogr2ogr, OGR_BY_EXTENSION, _ogr2ogr_cli, Ogr2OgrException
from hub.structures.file import FileGroup
import logging
import os


class Ogr2OgrUtilsTests(TestBase):

    def test_ogr_cli(self):
        """ Tests whether ogr2ogr is even executable
        """
        _ogr2ogr_cli(['--version'])
        self.assertRaises(Ogr2OgrException, lambda: _ogr2ogr_cli([]))

    def test_all_to_all(self):
        """ Converts from all supported types into all supported types
        """
        for ext_from, ogr_format_from in OGR_BY_EXTENSION.iteritems():
            data_dir = self.get_test_file_path(ext_from.lower())
            file_group_from = FileGroup.from_files(*(os.path.join(data_dir, f) for f in os.listdir(data_dir)))

            for ext_to, ogr_format_to in OGR_BY_EXTENSION.iteritems():
                logging.info('Converting from %s to %s', ext_from, ext_to)
                file_group_to = ogr2ogr(file_group_from, ogr_format_to)
                # todo
                # self.assertIn('Bahnhoefe', [os.path.splitext(fn)[0] for fn in file_group_to.names])

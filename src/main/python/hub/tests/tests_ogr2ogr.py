# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Tests for ogr2ogr wrapper/utility
"""

import logging

import os

from hub.tests.testutils import TestBase
from hub.utils.ogr2ogr import ogr2ogr, OgrFormat, _ogr2ogr_cli, Ogr2OgrException, WFS, GPKG
from hub.structures.file import FileGroup

logger = logging.getLogger(__name__)


class Ogr2OgrUtilsTests(TestBase):
    def test_ogr_cli(self):
        """ Tests whether ogr2ogr is even executable
        """
        _ogr2ogr_cli(['--version'])
        self.assertRaises(Ogr2OgrException, lambda: _ogr2ogr_cli([]))

    def test_all_to_all(self):
        """ Converts from all supported types into all supported types
        """
        # Disable some formats:
        # - WFS: read-only format
        # - GPKG/GeoPackage: Support in GDAL 1.11.1 is extremely lacking # GDAL2
        formats = set(OgrFormat.formats) - {WFS, GPKG}
        for ogr_format_from in formats:
            data_dir = self.get_test_file_path(ogr_format_from.extension[0].lower())

            file_group_from = FileGroup.from_files(*(os.path.join(data_dir, f) for f in os.listdir(data_dir)))

            for ogr_format_to in formats:
                logger.info('Converting from %s to %s', ogr_format_from.identifier, ogr_format_to.identifier)
                ogr2ogr(file_group_from, ogr_format_to)

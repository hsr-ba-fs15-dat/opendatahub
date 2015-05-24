# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hub.formats import Format

from hub.utils import ogr2ogr

if 'Interlis 1' in ogr2ogr.SUPPORTED_DRIVERS:
    class INTERLIS1(Format):
        label = 'INTERLIS 1'
        ogr_format = ogr2ogr.INTERLIS_1

        description = """
        INTERLIS ist ein Dateiformat zum Austausch von Geodaten.
        """

        extension = 'itf'

        @classmethod
        def is_format(cls, file, *args, **kwargs):
            return file.extension == cls.extension

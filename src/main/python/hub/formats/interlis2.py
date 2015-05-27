# -*- coding: utf-8 -*-
""" Interlis 2 support. Currently disabled. """

from __future__ import unicode_literals

# Note: Interlis 2 is not supported at this time due to issues with the format support in ogr2ogr.

# from hub.formats import Format
# from hub.utils import ogr2ogr
#
# if 'Interlis 2' in ogr2ogr.SUPPORTED_DRIVERS:
#     class INTERLIS2(Format):
#         label = 'INTERLIS 2'
#         description = """
#         INTERLIS ist ein Dateiformat zum Austausch von Geodaten.
#         """
#
#         extension = 'xtf'
#
#         is_export_format = False
#
#         @classmethod
#         def is_format(cls, file, *args, **kwargs):
#             return file.extension == 'xtf'

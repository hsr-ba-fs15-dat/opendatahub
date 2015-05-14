# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hub.formats import Format

"""
"""


class INTERLIS2(Format):
    label = 'INTERLIS 2'
    description = """
    INTERLIS ist ein Dateiformat zum Austausch von Geodaten.
    """

    is_export_format = False

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'xtf'

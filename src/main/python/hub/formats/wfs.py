# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from hub.formats import Format


class WFS(Format):
    label = 'WFS'
    description = """
    Web Feature Service ist ein Web Service-Protokoll fúr Geo-Daten.
    """

    is_export_format = False

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return False

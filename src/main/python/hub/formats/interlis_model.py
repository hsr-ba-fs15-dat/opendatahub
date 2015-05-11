# encoding=utf-8
from __future__ import unicode_literals

from .base import Format


class InterlisModelFormat(Format):
    name = 'Interlis1Model'
    label = 'Interlis 1 Modell (ili)'
    description = 'Modell für Interlis 1. Dies wird automatisch generiert aus den vorhandenen Daten und ' \
                  'sollte von Hand korrigiert werden'

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        # ILI is a write-only format for the moment, so identifying it doesn't help us, really.
        return False

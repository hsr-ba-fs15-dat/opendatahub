# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import math

import re

from hub.formats import Format, Formatter
from hub.structures.file import File
from hub.structures.frame import OdhType


class InterlisModelFormat(Format):
    name = 'INTERLIS1Model'
    label = 'INTERLIS 1 Modell (ili)'
    description = """
    Modell für INTERLIS 1. Dies wird automatisch generiert aus den vorhandenen Daten und sollte von Hand korrigiert
    werden
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        # ILI is a write-only format for the moment, so identifying it doesn't help us, really.
        return False


class InterlisModelFormatter(Formatter):
    targets = InterlisModelFormat,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        tables = []
        for df in dfs:
            tables.append(Table(df.name, df))
        model = Model(name, [Topic(name, tables)])

        return [File.from_string(name + '.ili', model.get_model_definition()).file_group]


class Model(object):
    def __init__(self, name, topics):
        self.name = sanitize_name(name)
        self.topics = topics

    def get_model_definition(self):
        result = 'TRANSFER {}; \n\n'.format(self.name)
        result += '!! ACHTUNG: Dies ist ein automatisch generiertes Modell und sollte nicht ohne Anpassungen \n'
        result += '!! verwendet werden.\n\n'

        domain = {}
        for topic in self.topics:
            for table in topic.tables:
                domain.update(table.domain)

        if len(domain) > 0:
            result += 'DOMAIN\n\n'

            for k, v in domain.iteritems():
                result += '\t{} = {};\n'.format(k, v)

        result += '\nMODEL {}\n\n'.format(self.name)

        for topic in self.topics:
            result += topic.get_topic_definition()

        result += '\nEND {}.\n\n'.format(self.name)

        result += 'FORMAT FREE;\n\n'

        result += '\nCODE\n\tBLANK = DEFAULT, UNDEFINED = DEFAULT, CONTINUE = DEFAULT;\n\t TID = ANY;\n\nEND.'

        return result


class Topic(object):
    def __init__(self, name, tables):
        self.name = sanitize_name(name)
        self.tables = tables

    def get_topic_definition(self):
        result = 'TOPIC {} = \n\n'.format(self.name)

        for table in self.tables:
            result += table.get_table_definition()

        result += '\nEND {}.\n'.format(self.name)
        return result


class Table(object):
    def __init__(self, name, df):
        self.name = sanitize_name(name)
        self.df = df
        self.fields, self.domain = self.get_fields()

    def get_table_definition(self):
        result = '\tTABLE {} = \n'.format(self.name)

        for field in self.fields:
            result += '\t\t{}: {};\n'.format(sanitize_name(field[0]), field[1])

        result += '\tNO IDENT\n'
        result += '\tEND {};\n'.format(self.name)
        return result

    def next_nines(self, x):
        '''
        results in the next series of 999...
        '''
        return int(10 ** (math.floor(math.log10(x) + 1)) - 1)

    def get_fields(self):
        domain = {}
        fields = []

        for name in self.df.columns:
            type = self.df[name].odh_type

            ili_type = '!! Unbekannter Typ'
            if type == OdhType.TEXT:
                max_length = self.df[name].str.len().max() if self.df[name].any() else 10

                ili_type = 'TEXT*{}'.format(int(max_length))
            elif type in (OdhType.INTEGER, OdhType.BIGINT, OdhType.SMALLINT):

                min = self.df[name].min()
                min = -self.next_nines(-min) if min and min < 0 else 0

                max = self.df[name].max()
                max = self.next_nines(max) if max and max > 0 else 0

                ili_type = '[{} .. {}]'.format(min, max)
            elif type == OdhType.FLOAT:
                max = self.df[name].max()
                max = self.next_nines(max) if max and max > 0 else 0

                ili_type = '[0.000 .. {}.999]'.format(max)
            elif type == OdhType.BOOLEAN:
                ili_type = 'BOOLEAN'
                domain['BOOLEAN'] = '(True, False)'
            elif type == OdhType.DATETIME:
                ili_type = 'DATE'  # actually, this can't include time in interlis. oh well.
            else:
                first_valid = self.df[name].first_valid_index()
                if type == OdhType.GEOMETRY and first_valid is not None:
                    import shapely.geometry as shp

                    value = self.df[name][first_valid]

                    if isinstance(value, shp.Point):
                        ili_type = 'POINT'
                        domain['POINT'] = 'COORD2 480000.000 70000.000 850000.000 310000.000'
                    elif isinstance(value, (shp.LineString, shp.LinearRing)):
                        ili_type = ('POLYLINE WITH (STRAIGHTS) '
                                    'VERTEX COORD2 480000.000 70000.000 850000.000 310000.000 '
                                    'WITHOUT OVERLAPS > 0.001')
                    elif isinstance(value, shp.Polygon):
                        ili_type = ('AREA WITH (STRAIGHTS) '
                                    'VERTEX COORD2 480000.000 70000.000 850000.000 310000.000 '
                                    'WITHOUT OVERLAPS > 0.001')
                    else:
                        ili_type = '!! Geometrie-Feld'

            optional = 'OPTIONAL ' if self.df[name].isnull().any() else ''
            fields.append((name, optional + ili_type))

        return fields, domain


def sanitize_name(name):
    sanitized = re.sub(r'[^A-Za-z0-9_\s]', '', name)
    return ''.join([s.capitalize() for s in re.split(r'\s', sanitized.strip())])

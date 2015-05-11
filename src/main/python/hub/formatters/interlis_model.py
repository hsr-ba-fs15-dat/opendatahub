import math

from django.utils.text import slugify

from hub.structures.frame import OdhType
from hub.structures.file import File
from .base import Formatter
from hub.formats import InterlisModelFormat


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
        self.name = slugify(unicode(name))
        self.topics = topics

    def get_model_definition(self):
        result = 'TRANSFER {}; \n\n'.format(self.name)
        result += '!! ACHTUNG: Dies ist ein automatisch generiertes Modell und sollte nicht ohne Anpassungen \n'
        result += '!! verwendet werden.\n\n'

        result += 'DOMAIN\n\n'

        domain = {}
        for topic in self.topics:
            for table in topic.tables:
                domain.update(table.domain)

        for k, v in domain.iteritems():
            result += "\t{}: {};\n".format(k, v)

        result += "\n\nMODEL {}\n\n".format(self.name)

        for topic in self.topics:
            result += topic.get_topic_definition()

        result += "\nEND {}.\n\n".format(self.name)

        result += "\nCODE\n\tBLANK = DEFAULT, UNDEFINED = DEFAULT, CONTINUE = DEFAULT;\n\t TID = ANY;\n\nEND."

        return result


class Topic(object):
    def __init__(self, name, tables):
        self.name = slugify(unicode(name))
        self.tables = tables

    def get_topic_definition(self):
        result = "TOPIC {}\n\n".format(self.name)

        for table in self.tables:
            result += table.get_table_definition()

        result += "\nEND {}.\n".format(self.name)
        return result


class Table(object):
    def __init__(self, name, df):
        self.name = slugify(unicode(name))
        self.df = df
        self.fields, self.domain = self.get_fields()

    def get_table_definition(self):
        result = "\tTABLE {} = \n".format(self.name)

        for field in self.fields:
            result += "\t\t{}: {};\n".format(slugify(field[0]), field[1])

        result += "\tNO IDENT\n"
        result += "\tEND {}.\n".format(self.name)
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
            if type == OdhType.TEXT:
                max_length = self.df[name].str.len().max() if self.df[name].any() else 0

                fields.append((name, "TEXT*{}".format(max_length)))
            elif type in (OdhType.INTEGER, OdhType.BIGINT, OdhType.SMALLINT):

                min = self.df[name].min()
                min = -self.next_nines(-min) if min and min < 0 else 0

                max = self.df[name].max()
                max = self.next_nines(max) if max and max > 0 else 0

                fields.append((name, "[{} .. {}]".format(min, max)))
            elif type == OdhType.FLOAT:
                max = self.df[name].max()
                max = self.next_nines(max) if max and max > 0 else 0

                fields.append((name, '[0.000 .. {}.999]'.format(max)))
            elif type == OdhType.DATETIME:
                fields.append((name, "DATE"))  # actually, this can't include time in interlis. oh well.
            else:
                first_valid = self.df[name].first_valid_index()
                if type == OdhType.GEOMETRY and first_valid is not None:
                    import shapely.geometry as shp

                    value = self.df[name][first_valid]

                    if isinstance(value, shp.Point):
                        fields.append((name, 'POINT'))
                        domain['POINT'] = 'COORD2 480000.000 70000.000 850000.000 310000.000'
                    elif isinstance(value, (shp.LineString, shp.LinearRing)):
                        fields.append((name, 'POLYLINE WITH (\'STRAIGHTS\') '
                                             'VERTEX COORD2 480000.000 70000.000 850000.000 310000.000'))
                    elif isinstance(value, shp.Polygon):
                        fields.append((name, 'AREA WITH (\'STRAIGHTS\') '
                                             'VERTEX COORD2 480000.000 70000.000 850000.000 310000.000'))
                    else:
                        raise RuntimeError('Unable to generate interlis model for data type {}'.format(type(value)))

        return fields, domain

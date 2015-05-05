from django.utils.text import slugify

from hub.models import TransformationModel, DocumentModel
from hub.utils.odhql import TransformationUtil
from hub.structures.frame import OdhType


class InterlisOneUtil(object):
    def generate_transfer_model(self, obj):
        return self.get_model(obj).get_model_definition()

    def get_model(self, obj):
        if isinstance(obj, TransformationModel):
            table = Table(obj.name, TransformationUtil.df_for_transformation(obj))
            topic = Topic(obj.name, [table])
            return Model(obj.name, [topic])
        elif isinstance(obj, DocumentModel):
            topics = []
            for fg in obj.groups.all():
                tables = []

                file_group = fg.to_file_group()
                dfs = file_group.to_df()
                for df in dfs:
                    tables.append(Table(df.name, df))
                topics.append(Topic(file_group.get_main_file().name, tables))
            return Model(obj.name, topics)

        raise RuntimeError('unknown model type: {}'.format(type(obj)))


class Model(object):
    def __init__(self, name, topics):
        self.name = slugify(name)
        self.topics = topics

    def get_model_definition(self):
        result = "TRANSFER {}; \n\nDOMAIN".format(self.name)
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
        self.name = slugify(name)
        self.tables = tables

    def get_topic_definition(self):
        result = "TOPIC {}\n\n".format(self.name)

        for table in self.tables:
            result += table.get_table_definition()

        result += "\nEND {}.\n".format(self.name)
        return result


class Table(object):
    def __init__(self, name, df):
        self.name = slugify(name)
        self.df = df
        self.fields, self.domain = self.get_fields()

    def get_table_definition(self):
        result = "\tTABLE {} = \n".format(self.name)

        for field in self.fields:
            result += "\t\t{}: {};\n".format(slugify(field[0]), field[1])

        result += "\tNO IDENT\n"
        result += "\tEND {}.\n".format(self.name)
        return result

    def get_fields(self):
        domain = {}
        fields = []

        for name in self.df.columns:
            type = self.df[name].odh_type
            if type == OdhType.TEXT:
                max_length = self.df[name].str.len().max() if self.df[name].any() else 0

                fields.append((name, "TEXT*{}".format(max_length)))
            elif type in (OdhType.INTEGER, OdhType.BIGINT, OdhType.SMALLINT):
                import math

                # results in the next series of 999...
                next_nines = lambda x: int(10 ** (math.floor(math.log10(x) + 1)) - 1)

                min = self.df[name].min()
                min = -next_nines(-min) if min and min < 0 else 0

                max = self.df[name].max()
                max = next_nines(max) if max and max > 0 else 0

                fields.append((name, "[{} .. {}]".format(min, max)))
            elif type == OdhType.DATETIME:
                fields.append((name, "DATE"))  # actually, this can't include time in interlis. oh well.
            else:
                first_valid = self.df[name].first_valid_index()
                if type == OdhType.GEOMETRY and first_valid is not None:
                    import shapely.geometry as shp

                    value = self.df[name][first_valid]

                    if isinstance(value, shp.Point):
                        fields.append((name, 'POINT'))
                        # FIXME this needs srid, right?
                        domain['POINT'] = 'COORD2 480000.000 70000.000 850000.000 310000.000'
                    elif isinstance(value, (shp.LineString, shp.LinearRing)):
                        fields.append((name, 'POLYLINE WITH (\'STRAIGHTS\') '
                                             'VERTEX COORD2 480000.000 70000.000 850000.000 310000.000'))
                    elif isinstance(value, shp.Polygon):
                        fields.appen((name, 'AREA WITH (\'STRAIGHTS\') '
                                            'VERTEX COORD2 480000.000 70000.000 850000.000 310000.000'))
                    else:
                        raise RuntimeError('Unable to generate interlis model for data type {}'.format(type(value)))

        return fields, domain


import django

django.setup()

model = TransformationModel.objects.get(id=20)
print InterlisOneUtil().generate_transfer_model(model)

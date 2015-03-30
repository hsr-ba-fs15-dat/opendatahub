"""

"""

from django.core.management.base import BaseCommand

from hub.tests.testutils import TestBase
from hub.models import DocumentModel, FileGroupModel, FileModel
from hub import formats
from hub.structures.file import FileGroup
import logging


logging.getLogger('django.db.backends').setLevel(logging.WARN)


class Command(BaseCommand):
    help = 'Loads test data into the database'

    IMPORT = {
        # first element in considered the main file
        ('mockaroo.com.csv',): formats.CSV,
        ('mockaroo.com.json',): formats.JSON,
        ('mockaroo.com.xlsx',): formats.Excel,
        ('gml/Bahnhoefe.gml', 'gml/Bahnhoefe.gfs', 'gml/Bahnhoefe.xsd',): formats.GML,
        ('json/Bahnhoefe.json',): formats.GeoJSON,
        ('kml/Bahnhoefe.kml',): formats.KML,
        ('shp/Bahnhoefe.shp', 'shp/Bahnhoefe.shx', 'shp/Bahnhoefe.dbf', 'shp/Bahnhoefe.ili'): formats.Shapefile,
    }

    def handle(self, *args, **options):
        user = TestBase.get_test_user()

        for files, format in self.IMPORT.iteritems():
            fg = FileGroup.from_files(*[TestBase.get_test_file_path(f) for f in files])

            doc = DocumentModel(name='Test {}'.format(', '.join(fg.names)),
                                description='Testdaten im {} Originalformat'.format(format.name),
                                private=False, owner=user)
            doc.save()

            file_group = FileGroupModel(document=doc, format=None)
            file_group.save()

            for f in fg:
                file_model = FileModel(file_name=f.name, data=f.stream.getvalue(), file_group=file_group)
                file_model.save()

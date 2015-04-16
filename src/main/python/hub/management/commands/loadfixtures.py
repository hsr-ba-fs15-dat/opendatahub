"""

"""

from django.core.management.base import BaseCommand

from hub.tests.testutils import TestBase
from hub.models import DocumentModel, FileGroupModel, FileModel
from hub import formats
from hub.structures.file import FileGroup
import logging
from django import db

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
        ('trobdb/Baustellen Februar 2015.xls',): formats.Excel,
        ('trobdb/TbaBaustellenZHWFS.gml', 'trobdb/TbaBaustellenZHWFS.xsd'): formats.GML,
        ('trobdb/tiefbaustelle.json',): formats.GeoJSON,
        ('trobdb/truckinfo.xml',): formats.XML,
        ('trobdb/Baustellen.kml',): formats.XML,
        ('perf/employees.csv',): formats.CSV,
        ('perf/children.csv',): formats.CSV,
        ('interlis1/Bahnhoefe.ili', 'interlis1/Bahnhoefe.itf'): formats.INTERLIS1,
        # ('interlis1/Bahnhoefe.ili', 'interlis1/Bahnhoefe.xml'): formats.INTERLIS2
    }

    def add_fg(self, fg, format, name=None, desc=None):
        name = name or 'Test {}'.format(', '.join(fg.names))

        if len(name) > 200:
            name = name[:197] + '...'

        desc = desc or 'Testdaten'
        doc = DocumentModel(name=name,
                            description=desc + ' (Originalformat: {})'.format(format.name),
                            private=False, owner=self.user)

        doc.save()

        file_group = FileGroupModel(document=doc, format=None)
        file_group.save()

        for f in fg:
            file_model = FileModel(file_name=f.name, data=f.stream.getvalue(), file_group=file_group)
            file_model.save()

        db.reset_queries()

    def handle(self, *args, **options):
        self.user = TestBase.get_test_user()

        for files, format in self.IMPORT.iteritems():
            fg = FileGroup.from_files(*[TestBase.get_test_file_path(f) for f in files])
            self.add_fg(fg, format)

        self.add_multiple(FileGroup.from_files(TestBase.get_test_file_path('perf/employees.csv')), formats.CSV, 10)
        self.add_multiple(FileGroup.from_files(TestBase.get_test_file_path('mockaroo.com.json')), formats.JSON, 500)

    def add_multiple(self, fg, format, n=100):
        for i in xrange(n):
            self.add_fg(fg, format, name='Dummy', desc='Filler data')

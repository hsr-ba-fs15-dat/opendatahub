# coding=utf-8
from __future__ import unicode_literals

"""

"""

import logging

from django.core.management.base import BaseCommand
from django import db
import codecs

from hub.tests.testutils import TestBase
from hub.models import DocumentModel, FileGroupModel, FileModel, UrlModel, TransformationModel
from hub import formats
from hub.structures.file import FileGroup
from hub.utils.odhql import TransformationUtil

logging.getLogger('django.db.backends').setLevel(logging.WARN)


class Command(BaseCommand):
    help = 'Loads test data into the database'

    IMPORT = [
        # first element in considered the main file
        (formats.CSV, 'mockaroo.com.csv',),
        (formats.JSON, 'mockaroo.com.json',),
        (formats.Excel, 'mockaroo.com.xlsx',),
        (formats.GML, 'gml/Bahnhoefe.gml', 'gml/Bahnhoefe.gfs', 'gml/Bahnhoefe.xsd',),
        (formats.GeoJSON, 'json/Bahnhoefe.json',),
        (formats.KML, 'kml/Bahnhoefe.kml',),
        (formats.Shapefile, 'shp/Bahnhoefe.shp', 'shp/Bahnhoefe.shx', 'shp/Bahnhoefe.dbf', 'shp/Bahnhoefe.ili'),
        (formats.Excel, 'trobdb/Baustellen Februar 2015.xls',),
        (formats.GML, 'trobdb/TbaBaustellenZHWFS.gml', 'trobdb/TbaBaustellenZHWFS.xsd'),
        (formats.GeoJSON, 'trobdb/tiefbaustelle.json',),
        (formats.XML, 'trobdb/truckinfo.xml',),
        (formats.KML, 'trobdb/Baustellen.kml',),
        (formats.CSV, 'perf/employees.csv',),
        (formats.CSV, 'perf/children.csv',),
        (formats.INTERLIS1, 'interlis1/Bahnhoefe.ili', 'interlis1/Bahnhoefe.itf'),
        (formats.Excel, 'trobdb/Baustellen Mai 2015.xls',),
        # ('interlis1/Bahnhoefe.ili', 'interlis1/Bahnhoefe.xml'): formats.INTERLIS2
    ]

    URLS = [
        ('http://maps.zh.ch/wfs/HaltestellenZHWFS', 'Haltestellen öffentlicher Verkehr ZH', formats.WFS),
        ('http://maps.zh.ch/wfs/TbaBaustellenZHWFS', 'Baustellen Kantonsstrassen ZH', formats.WFS)
    ]

    TRANSFORMATIONS = [
        ('trobdb/BaustellenExcel.odhql', 'TROBDB: Baustellen Februar 2015', 8),
        ('trobdb/tiefbaustelle-zh.odhql', 'TROBDB: Tiefbaustellen ZH (aus GeoJSON)', 10),
        ('trobdb/TruckInfo.odhql', 'TROBDB: TruckInfo', 11),
        ('trobdb/WFS-Baustellen-ZH.odhql', 'TROBDB: Baustellen Zürich (WFS)', 18),
        ('trobdb/Sanitize-Baustellen-kml.odhql', 'Sanitize Baustellen.kml', 12),
        ('trobdb/Baustellen-kml.odhql', 'TROBDB: Baustellen.kml', None)
    ]

    def add_document(self, desc, format, name):
        if len(name) > 200:
            name = name[:197] + '...'

        desc = desc or 'Testdaten'
        doc = DocumentModel(name=name,
                            description=desc + ' (Originalformat: {})'.format(format.name),
                            private=False, owner=self.user)
        doc.save()
        return doc

    def add_fg(self, fg, format, name=None, desc=None):
        doc = self.add_document(desc, format, name or 'Test {}'.format(', '.join(fg.names)))

        file_group = FileGroupModel(document=doc)
        file_group.save()
        for f in fg:
            file_model = FileModel(file_name=f.name, data=f.stream.getvalue(), file_group=file_group)
            file_model.save()

        file_group.to_file_group().to_df()  # force parse & caching

        db.reset_queries()

    def add_url(self, url, format, name=None, desc=None):
        doc = self.add_document(desc, format, name or 'Test {}'.format(url))

        file_group = FileGroupModel(document=doc)
        file_group.save()

        url_model = UrlModel(source_url=url, type='wfs' if format is formats.WFS else 'auto', file_group=file_group,
                             refresh_after=3600)
        url_model.save()

    def add_transformation(self, file, name, group=None, desc=None):

        with codecs.open(file, 'r', 'utf-8') as f:
            transformation = TransformationModel(name=name, description=desc or name, transformation=f.read(),
                                                 owner=self.user)
            transformation.save()

            if group:
                transformation.file_groups = FileGroupModel.objects.filter(id=group)
                transformation.save()

            TransformationUtil.df_for_transformation(transformation, self.user.id)

    def handle(self, *args, **options):
        self.user = TestBase.get_test_user()

        for args in self.IMPORT:
            it = iter(args)
            format = next(it)
            fg = FileGroup.from_files(*[TestBase.get_test_file_path(f) for f in it])
            self.add_fg(fg, format)

        for (url, name, format) in self.URLS:
            self.add_url(url, format, name=name)

        for (file, name, group) in self.TRANSFORMATIONS:
            self.add_transformation(TestBase.get_test_file_path(file), name, group)

        # self.add_multiple(FileGroup.from_files(TestBase.get_test_file_path('perf/employees.csv')), formats.CSV, 5)
        self.add_multiple(FileGroup.from_files(TestBase.get_test_file_path('mockaroo.com.json')), formats.JSON, 10)

    def add_multiple(self, fg, format, n=100):
        for i in xrange(n):
            self.add_fg(fg, format, name='Dummy', desc='Filler data')

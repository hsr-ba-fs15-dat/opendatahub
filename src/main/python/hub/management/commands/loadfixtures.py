# coding=utf-8
from __future__ import unicode_literals

"""

"""

import logging

from django.core.management.base import BaseCommand
from django import db
from django.utils import timezone

import codecs

from hub.tests.testutils import TestBase
from hub.models import DocumentModel, FileGroupModel, FileModel, UrlModel, TransformationModel
from hub import formats
from hub.structures.file import FileGroup
from hub.utils.odhql import TransformationUtil

from hub.odhql.interpreter import OdhQLInterpreter


logging.getLogger('django.db.backends').setLevel(logging.WARN)


class Command(BaseCommand):
    help = 'Loads test data into the database'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__()

        self.parse = kwargs.get('parse', True)

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
        (formats.Excel, 'trobdb/Baustellen Mai 2015.xls',)
        # ('interlis1/Bahnhoefe.ili', 'interlis1/Bahnhoefe.xml'): formats.INTERLIS2
    ]

    URLS = [
        ('http://maps.zh.ch/wfs/HaltestellenZHWFS', 'Haltestellen öffentlicher Verkehr ZH', formats.WFS),
        ('http://maps.zh.ch/wfs/TbaBaustellenZHWFS', 'Baustellen Kantonsstrassen ZH', formats.WFS)
    ]

    TRANSFORMATIONS = [
        ('trobdb/BaustellenExcel.odhql', 'TROBDB: Baustellen Februar 2015'),
        ('trobdb/tiefbaustelle-zh.odhql', 'TROBDB: Tiefbaustellen ZH (aus GeoJSON)'),
        ('trobdb/TruckInfo.odhql', 'TROBDB: TruckInfo'),
        ('trobdb/WFS-Baustellen-ZH.odhql', 'TROBDB: Baustellen Zürich (WFS)'),
        ('trobdb/Sanitize-Baustellen-kml.odhql', 'Sanitize Baustellen.kml'),
        ('trobdb/Baustellen-kml.odhql', 'TROBDB: Baustellen.kml'),
        ('trobdb/trobdb-union.odhql', 'TROBDB: Alle Daten'),
    ]

    def add_document(self, id, desc, format, name):
        if len(name) > 200:
            name = name[:197] + '...'

        desc = desc or 'Testdaten'
        doc = DocumentModel(id=id, name=name,
                            description=desc + ' (Originalformat: {})'.format(format.name),
                            private=False, created_at=timezone.now(), owner=self.user)
        doc.save()
        return doc

    def add_fg(self, id, fg, format, name=None, desc=None):
        doc = self.add_document(id, desc, format, name or 'Test {}'.format(', '.join(fg.names)))

        file_group = FileGroupModel(document=doc)
        file_group.save()
        for f in fg:
            file_model = FileModel(file_name=f.name, data=f.stream.getvalue(), file_group=file_group)
            file_model.save()

        if self.parse:
            file_group.to_file_group().to_df()  # force parse & caching

        db.reset_queries()

    def add_url(self, id, url, format, name=None, desc=None):
        doc = self.add_document(id, desc, format, name or 'Test {}'.format(url))

        file_group = FileGroupModel(document=doc)
        file_group.save()

        url_model = UrlModel(source_url=url, type='wfs' if format is formats.WFS else 'auto', file_group=file_group,
                             refresh_after=3600)
        url_model.save()

    def add_transformation(self, id, file, name, desc=None):

        with codecs.open(file, 'r', 'utf-8') as f:
            transformation = TransformationModel(id=id, name=name, description=desc or name, transformation=f.read(),
                                                 owner=self.user, created_at=timezone.now())
            transformation.save()

            file_groups, transformations = OdhQLInterpreter.parse_sources(transformation.transformation)

            if file_groups and len(file_groups) > 0:
                transformation.referenced_file_groups = FileGroupModel.objects.filter(id__in=file_groups.values())

            if transformations and len(transformations) > 0:
                transformation.referenced_transformations = TransformationModel.objects.filter(
                    id__in=transformations.values())

        if self.parse:
            TransformationUtil.df_for_transformation(transformation, self.user.id)

    def handle(self, *args, **options):
        self.user = TestBase.get_test_user()

        id = 0

        for args in self.IMPORT:
            it = iter(args)
            format = next(it)
            fg = FileGroup.from_files(*[TestBase.get_test_file_path(f) for f in it])

            id += 1

            self.add_fg(id, fg, format)

        id = 999

        for (url, name, format) in self.URLS:
            id += 1

            self.add_url(id, url, format, name=name)

        id = 1999

        for (file, name) in self.TRANSFORMATIONS:
            id += 1

            self.add_transformation(id, TestBase.get_test_file_path(file), name)

        id = 2999

        # self.add_multiple(id, FileGroup.from_files(TestBase.get_test_file_path('perf/employees.csv')), formats.CSV, 5)
        # id += 5
        self.add_multiple(id, FileGroup.from_files(TestBase.get_test_file_path('mockaroo.com.json')), formats.JSON, 10)

    def add_multiple(self, id, fg, format, n=100):
        for i in xrange(n):
            id += 1
            self.add_fg(id, fg, format, name='Dummy', desc='Filler data')

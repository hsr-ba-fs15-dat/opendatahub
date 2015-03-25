"""

"""

from django.core.management.base import BaseCommand
import os

from hub.tests.testutils import TestBase
from hub.models import DocumentModel, FileGroupModel, FileModel


class Command(BaseCommand):
    help = 'Loads test data into the database'

    def handle(self, *args, **options):
        user = TestBase.get_test_user()

        with open(TestBase.get_test_file_path('test-addresses.csv'), 'r') as f:
            doc = DocumentModel(name='Testdatei', description='Mit http://www.fakenamegenerator.com/ generierte Namen',
                                private=False, owner=user)
            doc.save()

            file_group = FileGroupModel(document=doc, format=None)
            file_group.save()

            file_model = FileModel(file_name=os.path.basename(f.name), data=f.read(), file_group=file_group)
            file_model.save()

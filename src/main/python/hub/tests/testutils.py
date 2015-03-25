"""

"""

import unittest

import os
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opendatahub.settings')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_DIR = os.path.join(BASE_DIR, 'temp')


class TestBase(unittest.TestCase):
    """

    """

    username = 'testdata_import'
    email = username + '@opendatahub.ch'
    password = 'secret'

    @classmethod
    def get_test_user(self):
        try:
            user = User.objects.get(username=self.username)
        except ObjectDoesNotExist:
            user = User.objects.create_user(username=self.username, email=self.email, password=self.password)

        return user

    @classmethod
    def get_test_file_path(cls, file_path):
        return os.path.join(BASE_DIR, 'testdata', *file_path.split('/'))

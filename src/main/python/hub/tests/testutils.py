"""

"""

import unittest

import os

from authentication.models import UserProfile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opendatahub.settings')

from django.core.exceptions import ObjectDoesNotExist


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_DIR = os.path.join(BASE_DIR, 'temp')


class TestBase(unittest.TestCase):
    """

    """

    username = 'testuser'
    email = username + '@opendatahub.ch'
    password = 'secret'

    @classmethod
    def get_test_user(self):
        try:
            user = UserProfile.objects.get(username=self.username)
        except ObjectDoesNotExist:
            user = UserProfile.objects.create_user(username=self.username, email=self.email, password=self.password)

        return user

    @classmethod
    def get_test_file_path(cls, file_path):
        return os.path.join(BASE_DIR, 'testdata', *file_path.split('/'))

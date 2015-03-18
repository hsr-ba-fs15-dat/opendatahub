"""

"""

import unittest
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opendatahub.settings')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_DIR = os.path.join(BASE_DIR, 'temp')


class TestBase(unittest.TestCase):
    """

    """

    @classmethod
    def get_test_file_path(cls, file_path):
        return os.path.join(BASE_DIR, 'testdata', *file_path.split('/'))

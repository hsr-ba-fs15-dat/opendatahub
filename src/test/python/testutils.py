"""

"""

import unittest
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opendatahub.settings')

base_dir = os.path.abspath(os.path.dirname(__file__))
temp_dir = os.path.join(base_dir, 'temp')


class TestBase(unittest.TestCase):
    """

    """


    @classmethod
    def get_test_file_path(cls, file_name):
        return os.path.join(base_dir, 'testdata', file_name)


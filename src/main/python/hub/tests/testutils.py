# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""

"""

import unittest

import os
from opendatahub.utils import cache

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opendatahub.settings')

from authentication.models import UserProfile

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
    def setUpClass(cls):
        cache.set = lambda *a, **k: None
        cache.get = lambda *a, **k: None
        cache.delete = lambda *a, **k: None

    @classmethod
    def get_test_user(cls):
        try:
            user = UserProfile.objects.get(username=cls.username)
        except ObjectDoesNotExist:
            user = UserProfile.objects.create_user(username=cls.username, email=cls.email, password=cls.password)

        return user

    @classmethod
    def get_test_file_path(cls, file_path):
        return os.path.join(BASE_DIR, 'testdata', *file_path.split('/'))

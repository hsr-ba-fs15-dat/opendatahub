# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
"""


class OdhQLExecutionException(Exception):
    pass


class TokenException(Exception):
    def __init__(self, message='parse error'):
        super(TokenException, self).__init__(message)

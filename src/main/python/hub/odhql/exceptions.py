# -*- coding: utf-8 -*-
from __future__ import unicode_literals

""" Exceptions for ODHQL stuff. """


class OdhQLExecutionException(Exception):
    """ Thrown on errors found during query execution. """
    pass


class TokenException(Exception):
    """
    Thrown when unexpected tokens are encountered in the parser. Note that this can't really happen in normal use;
    these exceptions are there for safe-guarding against mistakes when extending/maintaining the parser.
    """
    def __init__(self, message='parse error'):
        super(TokenException, self).__init__(message)

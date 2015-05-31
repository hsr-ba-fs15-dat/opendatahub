# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import contextlib
import logging

import warnings

""" OpenDataHub Exceptions and helper code. """


class OdhException(Exception):
    """ Root exception class for OpenDataHub specific exceptions
    """
    pass


class OdhWarning(Warning):
    """
    Root warning exception for OpenDataHub specific warnings. Any issued warning of this type will be displayed as
    a warning in the user interface.
    """
    pass


class OdhNotSupported(OdhException):
    """ Exception for unsupported operations of any kind (e.g. downloading in specific format does not work)
    """
    pass


def warn(message):
    """
    :type message: unicode
    """
    warnings.warn(OdhWarning(message))


@contextlib.contextmanager
def odh_warnings():
    """
    Usage:
    with odh_warnings as caught_warnings:
        # .. do something that can issue a warning
        print caught_warnings
    """
    filtered_warnings = []
    with warnings.catch_warnings(record=True) as all_warnings:
        yield filtered_warnings
        filtered_warnings.extend([w for w in all_warnings if isinstance(w.message, OdhWarning)])


class OdhLoggingHandler(logging.Handler):
    """
    Log handler for python logger with WARN severtiy which allows to auto-issue an warning (which will be displayed in
    the frontend) when extra={'frontend': True} is passed.
    """

    def emit(self, record):
        try:
            frontend = record.frontend
            if frontend:
                warn(record.getMessage())
        except Exception:
            pass

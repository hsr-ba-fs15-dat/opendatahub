# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import contextlib
import logging

import warnings


class OdhException(Exception):
    pass


class OdhWarning(Warning):
    pass


class OdhNotSupported(OdhException):
    pass


def warn(message):
    warnings.warn(OdhWarning(message))


@contextlib.contextmanager
def odh_warnings():
    filtered_warnings = []
    with warnings.catch_warnings(record=True) as all_warnings:
        yield filtered_warnings
        filtered_warnings.extend([w for w in all_warnings if isinstance(w.message, OdhWarning)])


class OdhLoggingHandler(logging.Handler):
    def emit(self, record):
        try:
            frontend = record.frontend
            if frontend:
                warn(record.getMessage())
        except Exception:
            pass

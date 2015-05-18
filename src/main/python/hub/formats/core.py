# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Base/infrastructure classes for formats and basic/builtin formats
"""

import sys
import traceback
import logging

from hub.structures.frame import OdhFrame
import hub.utils.common as com

from opendatahub.utils.plugins import RegistrationMixin
import collections

logger = logging.getLogger(__name__)


class NoFormatterException(Exception):
    pass


class FormattingException(Exception):
    pass


class Format(RegistrationMixin):
    """ Format base class. All classes that inherit from Format are automatically registered as formats.
    """

    # tells not to register as format
    _is_abstract = True

    # holds all registered formats by name
    formats = {}
    DEFAULT_FORMAT = None

    # descriptive meta information for display in webfrontend
    name = ''
    label = ''
    description = ''
    example = ''
    extension = ''

    is_export_format = True

    @classmethod
    def register_child(cls, name, bases, dct):
        # remove training whitespace cause by being a docstring/multiline comment
        cls.description = cls.description.strip()
        cls.example = cls.example.strip()
        cls.name = name
        if not dct.get('_is_abstract'):
            cls.formats[name] = cls

    @staticmethod
    def identify(file, *args, **kwargs):
        """ Tries to auto-detect the format by passing it through the chain of format classes
        :type file: hub.structures.File
        """
        try:
            return next((format for format in Format.formats.itervalues() if format.is_format(file, *args, **kwargs)))
        except StopIteration:
            return Format.DEFAULT_FORMAT

    @staticmethod
    def from_string(format):
        if isinstance(format, basestring):
            format = str(format).lower()
            try:
                format = next((f for f in Format.formats.itervalues() if format == f.__name__.lower()))
            except StopIteration:
                pass
        return format

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        raise NotImplementedError


class Other(Format):
    label = 'Original'

    description = """
    Die original zur Verfügung gestellten Daten ohne jegliche konversion.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return False


Format.DEFAULT_FORMAT = Other


class Formatter(RegistrationMixin):
    _is_abstract = True

    formatters = {}
    formatters_by_target = collections.defaultdict(list)

    targets = ()

    @classmethod
    def register_child(cls, name, bases, dct):
        if not dct.get('_is_abstract'):
            cls.formatters[name] = cls
            for format in cls.targets:
                cls.formatters_by_target[format].append(cls)

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        assert all([df.name for df in dfs]), 'DataFrame must have a name'
        exc_infos = []

        for formatter in cls.formatters_by_target[format]:
            try:
                result = com.ensure_tuple(formatter.format(dfs, name, format=format, *args, **kwargs))
                if not result:
                    raise FormattingException('Formatter did not return any result')
                return result
            except:
                exc_infos.append(sys.exc_info())
                continue

        if exc_infos:
            tbs = '\n'.join([''.join(traceback.format_exception(*ei)) for ei in exc_infos])
            logger.error('No formatter was able to format %s with target format %s:\n%s', name, format.__name__, tbs)
        raise NoFormatterException('Unable to format {} as {}'.format(name, format.name))


class NoParserException(Exception):
    pass


class ParsingException(Exception):
    pass


class Parser(RegistrationMixin):
    _is_abstract = True
    parsers = {}
    parsers_by_format = collections.defaultdict(list)

    accepts = ()

    @classmethod
    def register_child(cls, name, bases, dct):
        if not dct.get('_is_abstract'):
            cls.parsers[name] = cls
            for format in cls.accepts:
                cls.parsers_by_format[format].append(cls)

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        exc_infos = []
        for parser in cls.parsers_by_format[format]:
            try:
                dfs = com.ensure_tuple(parser.parse(file, format=format, *args, **kwargs))
                dfs = [OdhFrame.from_df(df, getattr(df, 'name', None) or file.basename) for df in dfs]
                if not dfs:
                    raise ParsingException('Parser did not return DataFrames')

                assert all([df.name for df in dfs]), 'DataFrame must have a name'
                assert len(set([df.name for df in dfs])) == len(dfs), 'Duplicate DataFrame names'
                return dfs
            except:
                exc_infos.append(sys.exc_info())
                continue

        if exc_infos:
            tbs = '\n'.join([''.join(traceback.format_exception(*ei)) for ei in exc_infos])
            logger.error('No parser was able to parse %s with format %s\n%s', file.name, format.__name__, tbs)

        raise NoParserException('Unable to parse data')

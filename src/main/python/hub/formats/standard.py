# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from opendatahub.utils.plugins import RegistrationMixin


class Format(RegistrationMixin):
    _is_abstract = True
    formats = {}
    DEFAULT_FORMAT = None

    label = ''
    descripttion = ''
    example = ''

    @classmethod
    def register_child(cls, name, bases, dct):
        if not dct.get('_is_abstract'):
            cls.formats[name] = cls

    @staticmethod
    def identify(stream, *args, **kwargs):
        try:
            return next((format for format in Format.formats.itervalues() if format.is_format(stream, *args, **kwargs)))
        except StopIteration:
            return Format.DEFAULT_FORMAT

    @classmethod
    def is_format(self, stream, *args, **kwargs):
        raise NotImplementedError


class CSV(Format):
    label = 'CSV'

    description = """
    Ein Datensatz pro Zeile und die Spalten durch Kommas getrennt.
    Die erste Zeile enthält die Namen der einzelnen Felder.
    """

    example = """
        Name,Vorname,Alter
        Scala,Fabio,24
        Hüsler,Christoph,27
        Liebi,Remo,26
    """

    @classmethod
    def is_format(self, stream, *args, **kwargs):
        return kwargs.get('name', '').endswith('.csv')


class JSON(Format):
    @classmethod
    def is_format(self, stream, *args, **kwargs):
        return kwargs.get('name', '').endswith('.json')


class Excel(Format):
    @classmethod
    def is_format(self, stream, *args, **kwargs):
        name = kwargs.get('name', '')
        return name.endswith('.xls') or name.endswith('.xlsx')


class Other(Format):

    @classmethod
    def is_format(self, stream, *args, **kwargs):
        return False

Format.DEFAULT_FORMAT = Other

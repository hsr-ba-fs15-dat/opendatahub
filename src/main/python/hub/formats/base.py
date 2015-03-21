# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from opendatahub.utils.plugins import RegistrationMixin


class Format(RegistrationMixin):
    _is_abstract = True
    formats = {}
    DEFAULT_FORMAT = None

    label = ''
    description = ''
    example = ''

    @classmethod
    def register_child(cls, name, bases, dct):
        if not dct.get('_is_abstract'):
            cls.formats[name] = cls

    @staticmethod
    def identify(file, *args, **kwargs):
        try:
            return next((format for format in Format.formats.itervalues() if format.is_format(file, *args, **kwargs)))
        except StopIteration:
            return Format.DEFAULT_FORMAT

    @classmethod
    def is_format(self, file, *args, **kwargs):
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
    def is_format(self, file, *args, **kwargs):
        return file.extension == 'csv'


class JSON(Format):
    @classmethod
    def is_format(self, file, *args, **kwargs):
        return file.extension == 'json'


class Excel(Format):
    @classmethod
    def is_format(self, file, *args, **kwargs):
        return file.extension in ('xls', 'xlsx')


class Shapefile(Format):

    label = 'ESRI Shapefile'

    description = """
    Ist ein ursprünglich für die Firma ESRI entwickeltes Format für Geodaten.
    """

    @classmethod
    def is_format(self, file, *args, **kwargs):
        return file.extension == 'shp'


class GML(Format):

    label = 'GML'

    description = """
    Geometry Markup Language (GML) ist ein Dateiformat zum Austausch von Geodaten.
    """

    @classmethod
    def is_format(self, file, *args, **kwargs):
        return file.extension == 'gml'


class KML(Format):

    label = 'KML'

    description = """
    Keyhole Markup Language (KML) ist ein Dateiformat zum Austausch von Geodaten. KML wurde durch die Verwendung in
    Google Earth bekannt.
    """

    @classmethod
    def is_format(self, file, *args, **kwargs):
        return file.extension == 'kml'


class INTERLIS1(Format):

    label = 'INTERLIS 1'

    description = """
    INTERLIS ist ein Dateiformat zum Austausch von Geodaten.
    """

    @classmethod
    def is_format(self, file, *args, **kwargs):
        return file.extension == 'itf'


class INTERLIS2(Format):

    label = 'INTERLIS 2'

    description = """
    INTERLIS ist ein Dateiformat zum Austausch von Geodaten.
    """

    @classmethod
    def is_format(self, file, *args, **kwargs):
        return file.extension == 'xtf'


class GeoJSON(Format):

    label = 'GeoJSON'

    description = """
    GeoJSON ist ein Dateiformat zum Austausch von Geodaten mittels JSON.
    """

    @classmethod
    def is_format(self, file, *args, **kwargs):
        return file.extension == 'json'


class Other(Format):

    @classmethod
    def is_format(self, file, *args, **kwargs):
        return False

Format.DEFAULT_FORMAT = Other

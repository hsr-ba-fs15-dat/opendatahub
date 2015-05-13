# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Base/infrastructure classes for formats and basic/builtin formats
"""

from opendatahub.utils.plugins import RegistrationMixin


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
    def is_format(cls, file, *args, **kwargs):
        extensions = [f.extension for f in file.file_group]
        return file.extension == 'csv' and not ('csvt' in extensions or 'prj' in extensions)


class JSON(Format):
    label = 'JSON'

    description = """
    JavaScript Objekt-Notation. Nützlich zur Wiederverwendung in Webapplikationen.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'json' and '"geometry"' not in file  # todo figure out a better way


class XML(Format):
    label = 'XML'

    description = """
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'xml'  # or '<?xml' in file  # do not uncomment, GML are xml too (and many more)


class Excel(Format):
    label = 'Excel'

    description = """
    Microsoft Office Excel Datei (xls bzw. xlsx)
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension in ('xls', 'xlsx')


class Shapefile(Format):
    label = 'ESRI Shapefile'

    description = """
    Ist ein ursprünglich für die Firma ESRI entwickeltes Format für Geodaten.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'shp'


class GML(Format):
    label = 'GML'

    description = """
    Geometry Markup Language (GML) ist ein Dateiformat zum Austausch von Geodaten.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'gml'


class KML(Format):
    label = 'KML'

    description = """
    Keyhole Markup Language (KML) ist ein Dateiformat zum Austausch von Geodaten. KML wurde durch die Verwendung in
    Google Earth bekannt.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'kml'


class INTERLIS1(Format):
    label = 'INTERLIS 1'

    description = """
    INTERLIS ist ein Dateiformat zum Austausch von Geodaten.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'itf' or file.extension == 'imd'


class INTERLIS2(Format):
    label = 'INTERLIS 2'
    description = """
    INTERLIS ist ein Dateiformat zum Austausch von Geodaten.
    """

    is_export_format = False

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'xtf'


class GeoJSON(Format):
    label = 'GeoJSON'

    description = """
    GeoJSON ist ein Dateiformat zum Austausch von Geodaten mittels JSON.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'geojson' or (
            file.extension == 'json' and '"geometry"' in file)  # todo figure out a better way


class WFS(Format):
    label = 'WFS'
    description = """
    Web Feature Service ist ein Web Service-Protokoll fúr Geo-Daten.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return False


# class GeoPackage(Format):
# label = 'GeoPackage'
# description = """
# GeoPackage ist ein Datenformat zum Austausch von Geodaten.
#     """
#
#     @classmethod
#     def is_format(cls, file, *args, **kwargs):
#         return file.extension == 'gpkg'


class GeoCSV(Format):
    label = 'GeoCSV'
    description = """
    Ist ein von dem HSR GeometaLab spezifiziertes, CSV-ähnliches Format für Geo-Daten.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return (file.extension == 'csv' and
                (file.basename + '.csvt' in file.file_group or file.basename + '.prj' in file.file_group)) or \
               (file.extension == 'geocsv')


class GeoPackage(Format):
    label = 'GeoPackage'
    description = '''
    Universelles Format für Vektor- und Raster-basierte Geo-Daten.
    '''

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == 'gpkg'


class Other(Format):
    label = 'Original'

    description = """
    Die original zur Verfügung gestellten Daten ohne jegliche konversion.
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return False


Format.DEFAULT_FORMAT = Other

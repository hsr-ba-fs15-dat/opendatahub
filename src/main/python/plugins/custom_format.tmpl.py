# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

"""
Example skeleton/template of a custom format implementation (parser and formatter). Copy this file and use a valid
Python module name (e.g. my_format.py). Your format will then be automatically loaded.
See hub.parsers package for concrete implementation examples.
"""

from hub.formats import Format, Formatter, Parser


class MyFormat(Format):
    """
    Example format class. Used to identify files, for format choice in the UI, etc.
    """

    label = 'MyFMT'

    description = """
    Kurze Beschreibung dieses Formats.
    """

    extension = 'myfmt'

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == cls.extension


class MyFormatFormatter(Formatter):
    """
    Example formatter class. These convert in-memory data (dataframes) into files a user can download/use.
    """
    targets = MyFormat,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        """
        :param dfs: List of DataFrames to format/convert
        :param name: Deprecated. Basename for the target file(s). Use df.name instead.
        :param format: Requested format. Useful if we can actually handle multiple formats.
        :return: One or a list of FileGroup objects
        """
        file_groups = []

        for df in dfs:
            pass  # do the magic here and append to file_groups

        return file_groups


class MyFormatParser(Parser):
    """
    Example parser class. These convert uploaded data into dataframes for further processing.
    """
    accepts = MyFormat,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        """
        :param file: The file identified by the format
        :param format: The format which matched (in case we accept multiple)
        :return: A DataFrame (GeoDataFrame for Geo Data)
        """
        fg = file.file_group  # file group contains all files with the same basename

        # do something with file.stream
        # or with each file in fg
        for f in fg:
            pass

        # parse data into one or multiple DataFrames
        dfs = []
        return dfs

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pandas as pd

from hub.formats import Format, Formatter, Parser
from hub.structures.file import File


class JSON(Format):
    label = 'JSON'

    description = """
    JavaScript Objekt-Notation. Nützlich zur Wiederverwendung in Webapplikationen.
    """

    extension = 'json'

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension == cls.extension and '"geometry"' not in file


class JSONFormatter(Formatter):
    targets = JSON,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        results = []

        for df in dfs:
            results.append(
                File.from_string(df.name + '.json', df.as_safe_serializable().to_json(orient='records')).file_group)
        return results


class JSONParser(Parser):
    accepts = JSON,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        return pd.read_json(file.stream)

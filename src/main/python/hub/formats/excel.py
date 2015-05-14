# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import tempfile

import pandas as pd

from hub.structures.file import File
from hub.formats import Formatter, Parser, Format


class Excel(Format):
    label = 'Excel'

    description = """
    Microsoft Office Excel Datei (xls bzw. xlsx)
    """

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        return file.extension in {'xls', 'xlsx'}


class ExcelFormatter(Formatter):
    targets = Excel,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        results = []

        for df in dfs:
            with tempfile.NamedTemporaryFile(suffix=".xlsx") as f:
                df.as_safe_serializable().to_excel(f.name, engine='xlsxwriter', index=False)
                f.seek(0)
                results.append(File.from_string(df.name + '.xlsx', f.read()).file_group)
        return results


class ExcelParser(Parser):
    accepts = Excel,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        return pd.read_excel(file.stream, encoding='UTF-8')
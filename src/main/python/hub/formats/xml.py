# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import etree

import re
import pandas as pd

from hub.formats import Format, Formatter, Parser
from hub.structures.file import File


class XML(Format):
    label = 'XML'

    description = """
    """

    extension = 'xml'

    @classmethod
    def is_format(cls, file, *args, **kwargs):
        # do not uncomment below, GML are XML too (and many more)
        return file.extension == cls.extension  # or '<?xml' in file


class XMLFormatter(Formatter):
    targets = XML,

    @classmethod
    def format(cls, dfs, name, format, *args, **kwargs):
        results = []

        for df in dfs:
            df = df.as_safe_serializable()
            root = etree.Element('root')
            for i, row in df.iterrows():
                attributes = {}
                for k, v in row.dropna().astype(unicode).to_dict().items():
                    k = re.sub(r'\W', '', k, flags=re.UNICODE)
                    attributes[k] = v

                etree.SubElement(root, 'row', attributes)

            results.append(File.from_string(df.name + '.' + XML.extension,
                                            etree.tostring(root, encoding='UTF-8', xml_declaration=True,
                                                           pretty_print=True)).file_group)
        return results


class GenericXMLParser(Parser):
    """ Flat XML parser
    """

    accepts = XML,

    @classmethod
    def parse(cls, file, format, *args, **kwargs):
        et = etree.parse(file.stream)
        return pd.DataFrame([dict(text=e.text, **e.attrib) for e in et.getroot()])

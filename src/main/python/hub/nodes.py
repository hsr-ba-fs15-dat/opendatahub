import json
import logging
import itertools

import types
import unicodecsv
import requests
import codecs

from hub import base
import hub.models


logger = logging.getLogger('hub.nodes')


class FileInput(base.InputNode):
    @classmethod
    def accept(cls, description):
        return isinstance(description, types.DictType) and 'file' in description

    def read(self, desc):
        for chunk in codecs.getreader('utf-8')(desc['file']):
            for line in chunk.splitlines():
                yield line.encode('utf8')


class HttpInput(base.InputNode):
    @classmethod
    def accept(cls, description):
        return isinstance(description, types.DictType) and 'url' in description and description['url'].startswith(
            'http')

    def read(self, desc):
        response = requests.get(desc['url'])

        logger.debug('http: requesting url %s', desc['url'])
        logger.debug('http: response status: %d', response.status_code)

        for line in response.text.splitlines():
            yield unicode(line).encode('utf-8')


class CsvInput(base.ParserNode):

    @classmethod
    def accept(cls, sample):
        return ',' in sample  # todo: better check

    def parse(self, input):
        csv_reader = unicodecsv.DictReader(input, encoding='utf-8')
        for row in csv_reader:
            yield row


class JsonInput(base.ParserNode):
    @classmethod
    def accept(cls, sample):
        return isinstance(sample, basestring) and sample.startswith('{')

    def parse(self, reader):
        try:
            for line in reader:
                yield json.loads(line)
        except:
            # assume it's just a string instead
            yield json.loads(reader)


class DatabaseWriter(base.OutputNode):
    def __init__(self, name, desc):
        self.desc = desc
        self.name = name

    def write(self, reader):
        doc = hub.models.DocumentModel(name=self.name, description=self.desc)
        doc.save()

        for record_content in reader:
            if not isinstance(record_content, types.DictType):
                raise RuntimeError('unexpected format')

            rec = hub.models.RecordModel(document=doc, content=record_content)
            rec.save()

        return doc


class DatabaseReader(base.InputNode):
    @classmethod
    def accept(cls, desc):
        return False

    def read(self, desc):
        for record in hub.models.RecordModel.objects.filter(document__id=desc['document_id']):
            yield record.content


class PlainOutput(base.FormatterNode):
    FORMAT = 'plain'

    def format(self, reader, out):
        for rec in reader:
            out.write(rec)
            out.write('\n')


class CsvOutput(base.FormatterNode):
    FORMAT = 'csv'

    def format(self, reader, out):
        peek = reader.next()

        writer = unicodecsv.DictWriter(out, fieldnames=peek.keys())
        writer.writeheader()

        for rec in itertools.chain([peek], reader):
            writer.writerow(rec)


class JsonOutput(base.FormatterNode):
    FORMAT = 'json'

    def format(self, reader, out):
        json.dump(list(reader), out)

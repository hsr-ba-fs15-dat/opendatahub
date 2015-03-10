import json
import logging

import unicodecsv
import requests

from hub import base
import hub.models


logger = logging.getLogger('hub.nodes')


class FileInput(base.InputNode):
    @classmethod
    def accept(cls, description):
        return description == 'file'

    def read(self, desc):
        with open(desc['file'], 'r') as file_input:
            for line in file_input:
                yield line


class HttpInput(base.InputNode):
    @classmethod
    def accept(cls, description):
        return type(description) == dict and 'url' in description and description['url'].startswith('http')

    def read(self, desc):
        response = requests.get(desc['url'])

        logger.debug('http: requesting url %s', desc['url'])
        logger.debug('http: response status: %d', response.status_code)

        for line in response.text.splitlines():
            yield line.encode('utf8')


class CsvInput(base.TransformationNode):
    @classmethod
    def accept(cls, sample):
        return ',' in sample  # todo: better check

    def transform(self, input):
        csv_reader = unicodecsv.DictReader(input, encoding='utf-8')
        for row in csv_reader:
            yield row


class JsonInput(base.TransformationNode):
    @classmethod
    def accept(cls, sample):
        return sample.startswith('{')

    def transform(self, reader):
        try:
            for line in reader:
                yield json.loads(line)
        except:
            # assume it's just a string instead
            yield json.loads(reader)


class DatabaseWriter(base.OutputNode):
    def __init__(self, desc):
        self.desc = desc

    def write(self, reader):
        doc = hub.models.DocumentModel(description=self.desc)
        doc.save()

        for record_content in reader:
            rec = hub.models.RecordModel(document=doc, content=record_content)
            rec.save()

        return doc


class DatabaseReader(base.InputNode):
    def __init__(self, document_id):
        self.document_id = document_id

    @classmethod
    def accept(cls, desc):
        return 'document_id' in desc

    def read(self, desc):
        for record in hub.models.RecordModel.objects.get(document_id=desc['document_id']):
            yield record.content

import csv
import json
from hub import base
import httplib2
import logging

import hub.models

logger = logging.getLogger('hub.nodes')


class FileInput(base.InputNode):
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        with open(self.filename, 'r') as file_input:
            for line in file_input:
                yield line


class HttpInput(base.InputNode):
    def __init__(self, url, method='GET', headers=None):
        self.url = url
        self.method = method
        self.headers = headers or {'Content-Type': 'application/json'}

    def read(self):
        if not self.url:
            raise RuntimeError('missing url')

        if not self.url.startswith('http'):
            return None # ??

        http = httplib2.Http()
        response, content = http.request(self.url, self.method, headers=self.headers)

        logger.debug('http: requesting url %s', self.url)
        logger.debug('http: response status: %d', response.status)

        return content


class CsvInput(base.TransformationNode):
    def transform(self, input):
        csv_reader = csv.DictReader(input.split('\n'))
        for row in csv_reader:
            yield row


class JsonInput(base.TransformationNode):
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


class DatabaseReader(base.InputNode):
    def __init__(self, document_id):
        self.document_id = document_id

    def read(self):
        for record in  hub.models.RecordModel.objects.get(document_id=self.document_id):
            yield record.content

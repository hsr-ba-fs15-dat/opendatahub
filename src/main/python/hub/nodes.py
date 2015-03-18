from hub.base import Formatter, FormatterDescription
import hub.models


class DatabaseWriter(object):
    def write(self, name, desc, data):
        doc = hub.models.DocumentModel(name=name, description=desc, content=data)
        doc.save()

        return doc


class DatabaseReader(object):
    def read(self, id):
        return hub.models.DocumentModel.objects.get(id=id)


class PlainOutput(Formatter):
    description = FormatterDescription('plain', 'Returns the document as-is', 'text/plain', 'txt')

    def format(self, document, writer, parameters):
        writer.write(document.content)

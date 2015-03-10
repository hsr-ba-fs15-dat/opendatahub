from django.db import models
import picklefield


def cap(str, length):
    return str if len(str) < length else str[0:length - 3] + '...'


class DocumentModel(models.Model):
    class Meta:
        db_table = 'hub_documents'

    description = models.TextField()

    def __str__(self):
        return "[Document id={} description={}]".format(self.id, cap(self.description, 50))


class RecordModel(models.Model):
    class Meta:
        db_table = 'hub_records'
        ordering = ['id']

    document = models.ForeignKey(DocumentModel, null=False, related_name='records')
    content = picklefield.PickledObjectField()

    def __str__(self):
        return "[Record id={} document={} content={}".format(self.id, self.document_id, cap(self.content, 50))

import base64

from django.db import models


def cap(str, length):
    return str if len(str) < length else str[:length - 3] + '...'


class DocumentModel(models.Model):
    class Meta:
        db_table = 'hub_documents'

    name = models.CharField(max_length=200)
    description = models.TextField()

    private = models.BooleanField(default=False)

    def __str__(self):
        return "[Document id={} description={}]".format(self.id, cap(self.description, 50))


# i really don't know how this will will work yet, it's more like a note
class FileGroupModel(models.Model):

    document = models.ForeignKey(DocumentModel)


class FileModel(models.Model):

    file_name = models.CharField(max_length=255)
    data = models.BinaryField()
    file_group = models.ForeignKey(FileGroupModel)

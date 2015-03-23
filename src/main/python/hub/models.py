"""

"""

from django.db import models


def cap(str, length):
    return str if len(str) < length else str[:length - 3] + '...'


class DocumentModel(models.Model):
    """
    Metadata for a document.
    """
    class Meta:
        db_table = 'hub_documents'

    name = models.CharField(max_length=200)
    description = models.TextField()

    private = models.BooleanField(default=False)

    #todo: ref to user for ownership

    def __str__(self):
        return "[Document id={} description={}]".format(self.id, cap(self.description, 50))


class FileGroupModel(models.Model):
    """
    Group of files belonging to each other.
    """
    document = models.ForeignKey(DocumentModel)
    format = models.CharField(max_length=50, null=True)


class FileModel(models.Model):
    """
    A single file.
    """
    file_name = models.CharField(max_length=255)
    data = models.BinaryField()
    file_group = models.ForeignKey(FileGroupModel)

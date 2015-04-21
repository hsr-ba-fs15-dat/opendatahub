"""

"""

from django.db import models

from opendatahub import settings
from hub.structures.file import File, FileGroup
from hub.utils.urlhandler import UrlHelper


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


def cap(str, length):
    return str if len(str) < length else str[:length - 3] + '...'


class DocumentModel(models.Model):
    """
    Metadata for a document.
    """

    class Meta(object):
        db_table = 'hub_documents'

    name = models.CharField(max_length=200)
    description = models.TextField()

    private = models.BooleanField(default=False)

    owner = models.ForeignKey(AUTH_USER_MODEL, null=True)

    def __str__(self):
        return "[Document id={} description={}]".format(self.id, cap(self.description, 50))


class FileGroupModel(models.Model):
    """
    Group of files belonging to each other.
    """
    document = models.ForeignKey(DocumentModel, related_name='groups')
    format = models.CharField(max_length=50, null=True)

    def to_file_group(self):
        group = FileGroup(id=self.id)
        group.add(*[f.to_file(group) for f in self.files.all()])

        group.add(*[u.to_file(group) for u in self.urls.all()])

        return group


class FileModel(models.Model):
    """
    A single file.
    """
    file_name = models.CharField(max_length=255)
    data = models.BinaryField()
    file_group = models.ForeignKey(FileGroupModel, related_name='files')

    def to_file(self, file_group=None):
        return File.from_string(self.file_name, self.data, file_group=file_group)


class UrlModel(models.Model):
    """
    Refreshable URL.
    """
    file_group = models.ForeignKey(FileGroupModel, related_name='urls')

    source_url = models.URLField()
    refresh_after = models.IntegerField(default=24 * 60 * 60)  # seconds
    type = models.CharField(max_length=10)

    format = models.CharField(max_length=50, null=True)

    def to_file(self, file_group=None):
        from hub.structures.file import WfsUrl

        if self.type == 'wfs':
            return WfsUrl('url%d' % self.id, self.source_url, file_group=file_group)
        else:
            name, data = UrlHelper().fetch_url(self)

            return File.from_string(name, data, file_group=file_group, format=self.format)


class TransformationModel(models.Model):
    """
    A transformation
    """
    name = models.CharField(max_length=255)
    transformation = models.TextField()
    description = models.TextField()
    private = models.BooleanField(default=False)
    owner = models.ForeignKey(AUTH_USER_MODEL, null=True)
    file_groups = models.ManyToManyField(FileGroupModel)

    def __str__(self):
        return "[Transformation id={} description={}".format(self.id, cap(self.description, 50))

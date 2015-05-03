'''

'''
from django.db import models
from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.db.models.query import QuerySet

from opendatahub import settings
from hub.structures.file import File, FileGroup


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


def cap(what, length):
    return what if len(what) < length else what[:length - 3] + '...'


class PackageModel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    private = models.BooleanField(default=False)

    owner = models.ForeignKey(AUTH_USER_MODEL)

    created_at = models.DateTimeField(auto_now_add=True)


class DocumentModel(PackageModel):
    """
    Metadata for a document.
    """


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
        from hub.structures.file import WfsUrl, Url

        if self.type == 'wfs':
            return WfsUrl('url%d' % self.id, self.source_url, cache_timeout=self.refresh_after, file_group=file_group)
        else:
            return Url('url%d' % self.id, self.source_url, format=self.format, cache_timeout=self.refresh_after,
                       file_group=file_group)


class TransformationModel(PackageModel):
    """
    A transformation
    """
    transformation = models.TextField()
    file_groups = models.ManyToManyField(FileGroupModel)


class InheritanceQuerySet(QuerySet):
    def select_subclasses(self, *subclasses):
        if not subclasses:
            subclasses = [o for o in dir(self.model)
                          if isinstance(getattr(self.model, o), SingleRelatedObjectDescriptor)
                          and issubclass(getattr(self.model, o).related.model, self.model)]
        new_qs = self.select_related(*subclasses)
        new_qs.subclasses = subclasses
        return new_qs

    def _clone(self, klass=None, setup=False, **kwargs):
        try:
            kwargs.update({'subclasses': self.subclasses})
        except AttributeError:
            pass
        return super(InheritanceQuerySet, self)._clone(klass, setup, **kwargs)

    def iterator(self):
        iter = super(InheritanceQuerySet, self).iterator()
        if getattr(self, 'subclasses', False):
            for obj in iter:
                obj = [getattr(obj, s) for s in self.subclasses if hasattr(obj, s)] or [obj]
                yield obj[0]
        else:
            for obj in iter:
                yield obj

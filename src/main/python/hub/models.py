# -*- coding: utf-8 -*-

"""
Django models.
"""

from __future__ import unicode_literals

from django.db import models
from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.db.models.query import QuerySet
from django.utils.text import slugify

from opendatahub import settings
from hub.structures.file import File, FileGroup
from hub.formats import Format, Other


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


def cap(what, length):
    """
    Limits string to a maximum length and appends three dots if the string length exceeds that limit.
    :param what: String to cap
    :param length: Length to cut off at
    """
    return what if len(what) < length else what[:length - 3] + '...'


class PackageModel(models.Model):
    """
    A package contains data - either a document or a transformation.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()

    private = models.BooleanField(default=False)

    owner = models.ForeignKey(AUTH_USER_MODEL)

    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)


class DocumentModel(PackageModel):
    """
    Metadata for a document.
    """

    def __unicode__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)


class FileGroupModel(models.Model):
    """
    Group of files belonging to each other.
    """
    document = models.ForeignKey(DocumentModel, related_name='groups')

    def to_file_group(self):
        group = FileGroup(id=self.id)

        group.add(*[f.to_file(group) for f in self.files.all()])

        group.add(*[u.to_file(group) for u in self.urls.all()])

        return group

    def __unicode__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)


class FileModel(models.Model):
    """
    A single file.
    """
    file_name = models.CharField(max_length=255)
    data = models.BinaryField()
    file_group = models.ForeignKey(FileGroupModel, related_name='files')
    format = models.CharField(max_length=50, null=True)

    def to_file(self, file_group=None):
        fmt = Format.from_string(self.format) if self.format else Other
        file = File.from_string(self.file_name, self.data, file_group=file_group)

        if fmt is not Other and fmt.is_format(file):
            file.format = fmt

        return file

    def __unicode__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)


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

        document_name = slugify(unicode(self.file_group.document.name))
        if self.type == 'wfs':
            return WfsUrl(document_name, self.source_url, cache_timeout=self.refresh_after, file_group=file_group)
        else:
            return Url(document_name, self.source_url, format=self.format, cache_timeout=self.refresh_after,
                       file_group=file_group)

    def __unicode__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)


class TransformationModel(PackageModel):
    """
    A transformation
    """
    transformation = models.TextField()

    is_template = models.BooleanField(default=False, null=False)

    referenced_file_groups = models.ManyToManyField(FileGroupModel, related_name='related_transformations')
    referenced_transformations = models.ManyToManyField('TransformationModel', related_name='related_transformations')

    def __unicode__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)


class InheritanceQuerySet(QuerySet):
    """
    Simplifies querying of package model above by automatically casting the models into their respective child classes.
    This is done using select_related in order to avoid n+1-query situations.

    Shamelessly lifted from http://jeffelmore.org/2010/11/11/automatic-downcasting-of-inherited-models-in-django/
    """
    subclasses = list()

    def select_subclasses(self, *subclasses):
        """
        Builds statement with all subclasses added to select_related.
        """
        if not subclasses:
            subclasses = [o for o in dir(self.model)
                          if isinstance(getattr(self.model, o), SingleRelatedObjectDescriptor)
                          and issubclass(getattr(self.model, o).related.model, self.model)]
        new_qs = self.select_related(*subclasses)
        new_qs.subclasses = subclasses
        return new_qs

    def _clone(self, klass=None, setup=False, **kwargs):
        """
        Add subclasses to clones if available.
        """
        try:
            kwargs.update({'subclasses': self.subclasses})
        except AttributeError:
            pass
        return super(InheritanceQuerySet, self)._clone(klass, setup, **kwargs)

    def iterator(self):
        """
        Cast the returned objects to their actual class.
        """
        iter = super(InheritanceQuerySet, self).iterator()
        if getattr(self, 'subclasses', False):
            for obj in iter:
                obj = [getattr(obj, s) for s in self.subclasses if hasattr(obj, s)] or [obj]
                yield obj[0]
        else:
            for obj in iter:
                yield obj

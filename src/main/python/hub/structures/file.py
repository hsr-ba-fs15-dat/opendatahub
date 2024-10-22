# -*- coding: utf-8 -*-
from __future__ import unicode_literals

""" Contains file structures used for the different converters/parsers.
"""

from cStringIO import StringIO
import contextlib
import tempfile
import shutil

import codecs
import os
from django.utils.encoding import force_bytes


class FileGroup(object):
    """ Container/group for multiple in-memory files
    """

    def __init__(self, files=None, id=None):
        self.files = files or []
        self.id = id

    @classmethod
    def from_files(cls, *paths):
        fg = cls()
        fg.add(*[File.from_file(path, file_group=fg) for path in paths])
        return fg

    def add(self, *files):
        self.files.extend(files)

    def remove(self, name):
        self.files = [f for f in self.files if file.name != name]

    def get_by_name(self, name):
        try:
            return next(f for f in self.files if f.name == name)
        except StopIteration:
            return None

    def get_by_extension(self, extension):
        return [f for f in self.files if f.extension == extension]

    def get_main_file(self):
        try:
            return next(f for f in self.files if not issubclass(f.get_format(), formats.Other))
        except StopIteration:
            return None

    @property
    def names(self):
        return [f.name for f in self.files]

    def rename_all(self, basename):
        for f in self.files:
            f.basename = basename

    @contextlib.contextmanager
    def on_filesystem(self):
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp()
            for f in self.files:
                f.write_to(temp_dir)
            yield temp_dir
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir)

    def to_df(self, force=False):
        file = self.get_main_file() or self.files[0]
        return file.to_df(force)

    def to_format(self, format):
        file = self.get_main_file() or self.files[0]
        return file.to_format(format)

    def __contains__(self, item):
        return item in self.names

    def __iter__(self):
        return iter(self.files)

    def __getitem__(self, ix_or_key):
        if isinstance(ix_or_key, int):
            return self.files[ix_or_key]
        elif isinstance(ix_or_key, basestring):
            return self.get_by_name(ix_or_key)

    def __repr__(self):
        return 'FileGroup({})'.format(', '.join([f.name for f in self.files]))


class File(object):
    """ In-memory file wrapper with added meta
    """

    CODEC = codecs.lookup('UTF-8')

    def __init__(self, name, stream, file_group=None, format=None, cache_timeout=None):
        if not file_group:
            file_group = FileGroup([self])

        if isinstance(name, str):
            name = unicode(name, 'UTF-8')

        self.name = name
        self._stream = stream
        self.file_group = file_group
        self.format = formats.Format.from_string(format) if isinstance(format, basestring) else format
        self.dfs = None
        self.cache_timeout = cache_timeout

    @classmethod
    def from_file(cls, path, *args, **kwargs):
        with open(path, 'rb') as f:
            file = cls(os.path.basename(path), StringIO(f.read()), *args, **kwargs)

        if not file.format:
            file.format = formats.identify(file)

        return file

    @classmethod
    def from_string(cls, name, string, *args, **kwargs):
        return cls(name, StringIO(force_bytes(string)), *args, **kwargs)

    @property
    def basename(self):
        return os.path.splitext(self.name)[0]

    @basename.setter
    def basename(self, basename):
        ext = self.extension
        self.name = '{}{}{}'.format(basename, bool(ext) * '.', ext)

    @property
    def extension(self):
        split = self.name.rsplit('.', 1)
        return split[-1].lower() if len(split) > 1 else ''

    @extension.setter
    def extension(self, ext):
        ext = ext or ''
        self.name = '{}{}{}'.format(self.basename, bool(ext) * '.', ext)

    @property
    def stream(self):
        self._stream.seek(0)
        return self._stream

    @property
    def ustream(self):
        return codecs.StreamReaderWriter(self.stream, self.CODEC.streamreader, self.CODEC.streamwriter)

    def write_to(self, dir):
        with open(os.path.join(dir, self.name), 'wb') as temp_f:
            temp_f.write(self.stream.getvalue())

    def get_format(self):
        if not self.format:
            self.format = formats.identify(self)

        return self.format

    def to_df(self, force=False):
        from opendatahub.utils import cache

        id_ = self.file_group.id
        invalidate = False

        if self.dfs is None:
            if not force and id_ is not None:
                cached = cache.get(('FG', id_))
                if cached is not None:
                    self.dfs = cached

            if self.dfs is None:
                from hub.formats import identify, parse

                format = self.format or identify(self)
                if not format:
                    return None
                self.dfs = parse(self, format)

                invalidate = True

        if invalidate and id_:
            params = {}
            if self.cache_timeout:
                params['timeout'] = self.cache_timeout

            cache.set(('FG', id_), self.dfs, **params)

            from hub.utils.odhql import TransformationUtil

            TransformationUtil.invalidate_related_cache(file_groups={id_})

        assert all([df.name for df in self.dfs]), 'DataFrame must have a name'
        return self.dfs

    def to_serializable_df(self):
        return [df.as_safe_serializable() for df in self.to_df()]

    def to_format(self, format):

        return formats.format(self.to_df(), self.basename, formats.Format.from_string(format))

    def __contains__(self, string):
        return string in self.ustream.read()

    def __repr__(self):
        return 'File({})'.format(self.name)


class WfsUrl(File):
    def __init__(self, name, url, *args, **kwargs):
        super(WfsUrl, self).__init__(name, None, format=formats.WFS, *args, **kwargs)

        self.url = url

    def write_to(self, dir):
        pass


class Url(File):
    def __init__(self, name, url, *args, **kwargs):
        super(Url, self).__init__(name, None, *args, **kwargs)
        self.url = url

    @property
    def stream(self):
        from hub.utils.urlhandler import UrlHelper

        data = UrlHelper().fetch_url(self.url, self.cache_timeout)

        return StringIO(data)

# leave at end to avoid circular imports
from hub import formats

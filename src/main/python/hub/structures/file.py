""" Contains file structures used for the different converters/parsers.
"""

from cStringIO import StringIO
import codecs
import contextlib
import tempfile
import shutil

import os

import pandas
from django.utils.encoding import force_bytes
from hub import formats
from django.core.cache import caches  # noqa


class FileGroup(object):
    """ Container/group for multiple in-memory files
    """

    def __init__(self, files=None):
        self.files = files or []

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
            return next((f for f in self.files if f.name == name))
        except StopIteration:
            return None

    def get_by_extension(self, extension):
        return [f for f in self.files if f.extension == extension]

    def get_main_file(self):
        return next((f for f in self.files if not issubclass(f.get_format(), formats.Other)))

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
                with open(os.path.join(temp_dir, f.name), 'wb') as temp_f:
                    temp_f.write(f.stream.getvalue())
            yield temp_dir
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir)

    def to_df(self, force=False):
        file = self.get_main_file()
        if file:
            return file.to_df(force)
        return None

    def to_format(self, format):
        file = self.get_main_file()
        if file:
            return file.to_format(format)
        return None

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

    def __init__(self, name, stream, file_group=None, format=None):
        if not file_group:
            file_group = FileGroup([self])

        self.name = name
        self._stream = stream
        self.file_group = file_group
        self.format = format
        self.df = None

    @classmethod
    def from_file(cls, path, *args, **kwargs):
        with open(path, 'rb') as f:
            return cls(os.path.basename(path), StringIO(f.read()), *args, **kwargs)

    @classmethod
    def from_string(cls, name, string, *args, **kwargs):
        return cls(name, StringIO(force_bytes(string)), *args, **kwargs)

    @property
    def basename(self):
        return os.path.splitext(self.name)[0]

    @basename.setter
    def basename(self, basename):
        ext = self.extension
        self.name = '{}{}{}'.format(self.basename, bool(ext) * '.', ext)

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

    def get_format(self):
        if not self.format:
            self.format = formats.identify(self)

        return self.format

    def to_df(self, force=False):
        if force or self.df is None:
            from hub import parsers

            format = formats.identify(self)
            if not format:
                return None

            self.df = parsers.parse(self, format)

        return self.df

    def to_normalized_df(self):
        """
        :return: DataFrame which contains only exportable data (no objects)
        """
        df = pandas.DataFrame(self.to_df().copy(True))
        for col in df.columns:
            temp = df[col].dropna()
            if len(temp) and temp.dtype == object and not isinstance(temp.iloc[0], unicode):
                try:
                    df[col] = df[col].astype(unicode)
                except:
                    pass

        return df

    def to_format(self, format):
        from hub import formatters, formats

        if isinstance(format, basestring):
            format = str(format).lower()
            try:
                format = next((f for f in formats.Format.formats.itervalues() if format == f.__name__.lower()))
            except StopIteration:
                raise  # todo

        return formatters.Formatter.format(self, format)

    def __contains__(self, string):
        return string in self.ustream.read()

    def __repr__(self):
        return 'File({})'.format(self.name)


if __name__ == '__main__':
    from hub.tests.testutils import TestBase

    files = (
        ('mockaroo.com.csv', formats.CSV),
        ('mockaroo.com.json', formats.JSON),
        ('gml/Bahnhoefe.gml', formats.GML),
        ('mockaroo.com.xls', formats.Excel),
    )

    for filename, cls in files:
        fg = FileGroup.from_files(TestBase.get_test_file_path(filename))

        f = fg[0]
        df = f.to_df()
        print df

        print f.to_format('gml').names

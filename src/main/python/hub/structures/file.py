""" Contains file structures used for the different converters/parsers.
"""

from cStringIO import StringIO
import contextlib
import tempfile
import shutil

import os

from hub import formats


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

    def __iter__(self):
        return iter(self.files)

    def __getitem__(self, ix_or_key):
        if isinstance(ix_or_key, int):
            return self.files[ix_or_key]
        elif isinstance(ix_or_key, basestring):
            return self.get_by_name(ix_or_key)
        raise ValueError

    @contextlib.contextmanager
    def on_filesystem(self):
        try:
            temp_dir = tempfile.mkdtemp()
            for f in self.files:
                with open(os.path.join(temp_dir, f.name), 'wb') as temp_f:
                    temp_f.write(f.stream.getvalue())
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir)


class File(object):
    """ In-memory file wrapper with added meta
    """

    def __init__(self, name, stream, file_group=None, format=None):
        if not file_group:
            file_group = FileGroup([self])

        self.name = name
        self.stream = stream
        self.file_group = file_group
        self.format = format
        self.df = None

    @classmethod
    def from_file(cls, path, *args, **kwargs):
        with open(path, 'rb') as f:
            return cls(os.path.basename(path), StringIO(f.read()), *args, **kwargs)

    @classmethod
    def from_string(cls, name, string, *args, **kwargs):
        return cls(name, StringIO(string), *args, **kwargs)

    @property
    def extension(self):
        return self.name.rsplit('.', 1)[-1].lower()


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

    def to_format(self, format):
        from hub import formatters, formats

        if not isinstance(format, formats.Format):
            format = str(format).lower()
            try:
                format = next((f for f in formats.Format.formats.itervalues() if format == f.__name__.lower()))
            except StopIteration:
                raise  # todo

        return formatters.Formatter.format(self, format)


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

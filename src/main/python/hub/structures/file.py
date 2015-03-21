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

    @property
    def names(self):
        return [f.name for f in self.files]

    def __iter__(self):
        return iter(self.files)

    def __getitem__(self, ixOrKey):
        if isinstance(ixOrKey, int):
            return self.files[ixOrKey]
        elif isinstance(ixOrKey, basestring):
            return self.get_by_name(ixOrKey)
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

    @classmethod
    def from_file(cls, path, *args, **kwargs):
        with open(path, 'rb') as f:
            return cls(os.path.basename(path), StringIO(f.read()), *args, **kwargs)

    @property
    def extension(self):
        return self.name.rsplit('.', 1)[-1].lower()

    def parse(self):
        from hub import parsers

        format = formats.identify(self)
        if not format:
            return None

        return parsers.parse(self, format)


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
        df = f.parse()
        print df

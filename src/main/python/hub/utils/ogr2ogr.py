"""
ogr2ogr (GDAL) command line interface wrapper
Requires ogr2ogr to be installed (e.g. sudo apt-get install gdal-bin)
"""

import subprocess
import collections
import shutil
import logging

import os
import types

from hub.structures.file import FileGroup


class Ogr2OgrException(Exception):
    pass


class OgrFormat(object):
    formats = []

    def __init__(self, extension, identifier, list_all):
        self.extension = extension if isinstance(extension, types.ListType) else [extension]
        self.identifier = identifier
        self.list_all = list_all

        self.formats.append(self)

    @classmethod
    def get_format(cls, file_group):
        for format in cls.formats:
            if any([len(file_group.get_by_extension(ext)) > 0 for ext in format.extension]):
                return format
        return None

    def __repr__(self):
        return '<OgrFormat identifier=\'{}\' extensions={} list_all={}>'.format(self.identifier, self.extension,
                                                                                self.list_all)


GML = OgrFormat('gml', 'GML', False)
SHP = OgrFormat('shp', 'ESRI Shapefile', False)
CSV = OgrFormat('csv', 'CSV', False)
GEO_JSON = OgrFormat('json', 'GeoJSON', False)
KML = OgrFormat('kml', 'KML', False)

INTERLIS_1 = OgrFormat(['itf', 'ili', 'imd'], 'Interlis 1', True)
INTERLIS_2 = OgrFormat(['xml', 'ili', 'imd'], 'Interlis 2', True)


def _ogr2ogr_cli(arguments, *args, **kwargs):
    cmd = ['ogr2ogr'] + arguments
    logging.debug('Running ogr2ogr: %s', ' '.join(cmd))
    process = subprocess.Popen(cmd)
    exit_code = process.wait()
    if exit_code:
        raise Ogr2OgrException(exit_code)


def ogr2ogr(file_group, to_type):
    assert (isinstance(file_group, FileGroup))

    from_format = OgrFormat.get_format(file_group)
    files_by_extension = (file for ext in from_format.extension
                          for file in file_group.get_by_extension(ext))

    main_file = next(files_by_extension)

    if from_format == to_type:
        return [file_group]

    with file_group.on_filesystem() as temp_dir:
        path = os.path.join(temp_dir, 'out')

        if from_format and from_format.list_all:
            _ogr2ogr_cli(['-f', to_type.identifier, path, ','.join([os.path.join(temp_dir, f.name)
                                                                    for f in file_group])])
        else:
            _ogr2ogr_cli(['-f', to_type.identifier, path, os.path.join(temp_dir, main_file.name)])

        files = []
        if os.path.isdir(path):
            files = [os.path.join(path, name) for name in os.listdir(path)]
        elif os.path.exists(path):
            for filename in os.listdir(temp_dir):
                if os.path.splitext(filename)[0] == 'out':
                    ext = to_type.extension[0] if filename == 'out' else os.path.splitext(filename)[1]

                    files.append(os.path.join(temp_dir, '{}.{}'.format(main_file.basename, ext)))
                    shutil.move(os.path.join(temp_dir, filename), files[-1])

        groups = collections.defaultdict(list)
        for file in files:
            groups[os.path.splitext(file)[0]].append(file)

        return [FileGroup.from_files(*f) for f in groups.values()]

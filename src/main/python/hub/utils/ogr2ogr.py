"""
ogr2ogr (GDAL) command line interface wrapper
Requires ogr2ogr to be installed (e.g. sudo apt-get install gdal-bin)
"""
from functools import partial
import subprocess
import collections
import shutil
import logging

import os
import types

from hub.structures.file import FileGroup, WfsUrl


logger = logging.getLogger(__name__)


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
        if len(file_group.files) == 1 and isinstance(file_group[0], WfsUrl):
            return WFS

        for format in cls.formats:
            if any([len(file_group.get_by_extension(ext)) > 0 for ext in format.extension]):
                return format
        return None

    def __repr__(self):
        return '<OgrFormat identifier=\'{}\' extensions={} list_all={}>'.format(self.identifier, self.extension,
                                                                                self.list_all)


GML = OgrFormat('gml', 'GML', False)
# GPKG = OgrFormat('gpkg', 'GPKG', False) # no driver?
SHP = OgrFormat('shp', 'ESRI Shapefile', False)
CSV = OgrFormat('csv', 'CSV', False)
GEO_JSON = OgrFormat('json', 'GeoJSON', False)
KML = OgrFormat('kml', 'KML', False)

WFS = OgrFormat('wfs', 'WFS', False)

INTERLIS_1 = OgrFormat(['itf', 'ili', 'imd'], 'Interlis 1', True)


def _ogr2ogr_cli(arguments, *args, **kwargs):
    cmd = ['ogr2ogr'] + arguments
    logger.debug('Running ogr2ogr: %s', ' '.join(cmd))
    try:
        output = subprocess.check_output(cmd)
        logger.debug(output)
    except subprocess.CalledProcessError as e:
        logger.error('%s: %s\n%s', e.returncode, e.cmd, e.output)
        raise Ogr2OgrException(e.returncode)


def ogr2ogr(file_group, to_type):
    assert (isinstance(file_group, FileGroup))

    from_format = OgrFormat.get_format(file_group)

    if from_format == to_type:
        return [file_group]

    with file_group.on_filesystem() as temp_dir:
        path = os.path.join(temp_dir, 'out')

        if from_format is WFS:
            _ogr2ogr_cli(['-f', to_type.identifier, path, 'WFS:{}'.format(file_group[0].url)])
        else:
            files_by_extension = (file for ext in from_format.extension
                                  for file in file_group.get_by_extension(ext))

            main_file = next(files_by_extension)

            if from_format and from_format.list_all:

                files = sorted([os.path.join(temp_dir, f.name) for f in file_group],
                               partial(sort_by_extension_index, from_format))

                _ogr2ogr_cli(['-f', to_type.identifier, path, ','.join(files)])
            else:
                _ogr2ogr_cli(['-f', to_type.identifier, path, os.path.join(temp_dir, main_file.name)])

        files = []
        if os.path.isdir(path):
            files = [os.path.join(path, name) for name in os.listdir(path)]
        elif os.path.exists(path):
            for filename in os.listdir(temp_dir):
                if os.path.splitext(filename)[0] == 'out':
                    ext = to_type.extension[0] if filename == 'out' else os.path.splitext(filename)[1]

                    files.append(
                        os.path.join(temp_dir, '{}.{}'.format(main_file.basename if main_file else 'out', ext)))
                    shutil.move(os.path.join(temp_dir, filename), files[-1])

        groups = collections.defaultdict(list)
        for file in files:
            groups[os.path.splitext(file)[0]].append(file)

        return [FileGroup.from_files(*f) for f in groups.values()]


def sort_by_extension_index(from_format, a, b):
    """
    force main file(s) to appear a) first and b) in the order specified in the format
    this is a hack to get interlis 1 to work reliably, as ogr2ogr appears to be a bit... touchy about that.

    :param from_format: detected format. used to get the extension list
    :param a: first object to compare
    :param b: second object to compare
    :return: -1, 0, 1 as usual for comparison functions.
    """
    get_extension_only = lambda ext: ext[1][1:] if ext and len(ext) > 1 else None

    ext_a = get_extension_only(os.path.splitext(a))
    ext_b = get_extension_only(os.path.splitext(b))

    if ext_a and ext_a in from_format.extension:
        if ext_b and ext_b in from_format.extension:
            return cmp(from_format.extension.index(ext_a), from_format.extension.index(ext_b))
        else:
            return -1

    if ext_b and ext_b in from_format.extension:
        return 1

    return cmp(a, b)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
ogr2ogr (GDAL) command line interface wrapper
Requires ogr2ogr to be installed (e.g. sudo apt-get install gdal-bin)
"""
from functools import partial
import subprocess
import collections
import shutil
import logging
import random
import string

import os

from hub.structures.file import FileGroup, WfsUrl
import hub.utils.common as com
import osgeo.ogr as ogr

logger = logging.getLogger(__name__)


class Ogr2OgrException(Exception):
    pass

# drivers/formats supported by the currently installed GDAL version
# will usually vary depending on how GDAL was compiled as it required many third party libraries/dependencies
# for various file formats.
SUPPORTED_DRIVERS = {ogr.GetDriver(i).GetName() for i in xrange(ogr.GetDriverCount())}


class OgrFormat(object):
    """
    Describes an ogr2ogr/GDAL supported format.
    """

    formats = []

    def __init__(self, extension, identifier, list_all, addtl_args=(), allowed_return_codes=()):
        self.extension = com.ensure_tuple(extension)
        self.identifier = identifier
        self.list_all = list_all
        self.addtl_args = com.ensure_tuple(addtl_args)
        self.allowed_return_codes = com.ensure_tuple(allowed_return_codes)
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
GPKG = OgrFormat('gpkg', 'GPKG', False)
SHP = OgrFormat('shp', 'ESRI Shapefile', False)
CSV = OgrFormat('csv', 'CSV', False)
GEO_JSON = OgrFormat('json', 'GeoJSON', False)
KML = OgrFormat('kml', 'KML', False)
WFS = OgrFormat('wfs', 'WFS', False)

INTERLIS_1 = OgrFormat(['itf', 'ili', 'imd'], 'Interlis 1', True)


def _rand_string(n):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))


def _ogr2ogr_cli(arguments, log_on_error=True, allowed_return_codes=(), *args, **kwargs):
    """ Executes ogr2ogr CLI installed on system. Make sure this binary is available and in PATH.
    :param log_on_error: Whether we should log errors
    :param allowed_return_codes: Return codes which should not be regarded as errors
    :type arguments: list
    :type log_on_error: bool
    :type allowed_return_codes: tuple
    """
    cmd = ['ogr2ogr'] + arguments
    logger.debug('Running ogr2ogr: %s', ' '.join(cmd))
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        logger.debug(output)
    except subprocess.CalledProcessError as e:
        if e.returncode not in allowed_return_codes:
            if log_on_error:
                logger.error('%s: %s\n%s', e.returncode, e.cmd, e.output)
            raise Ogr2OgrException(e.returncode)


def ogr2ogr(file_group, to_type, addtl_args=(), *args, **kwargs):
    """
    Helper utitility for converting in-memory files with ogr2ogr. These are temporarily written to file system in order
    order to make the accessible to ogr2ogr.
    :type file_group: hub.structures.file.FileGroup
    :type to_type: hub.utils.ogr2ogr.OgrFormat
    :type addtl_args: tuple or list
    :param args: Additional args passed to _ogr2ogr_cli function.
    :param kwargs: Additional args passed to _ogr2ogr_cli function.
    """
    kwargs.setdefault('allowed_return_codes', to_type.allowed_return_codes)
    assert isinstance(file_group, FileGroup)

    from_format = OgrFormat.get_format(file_group)

    if from_format == to_type:
        return [file_group]

    with file_group.on_filesystem() as temp_dir:
        out_path = os.path.join(temp_dir, _rand_string(24))
        os.mkdir(out_path)
        path = os.path.join(out_path, 'out')

        if from_format is WFS:
            _ogr2ogr_cli(['-f', to_type.identifier, path, 'WFS:{}'.format(file_group[0].url)], *args, **kwargs)
            main_file = None
        else:
            files_by_extension = (file for ext in from_format.extension
                                  for file in file_group.get_by_extension(ext))

            main_file = next(files_by_extension)

            ogr2ogr_args = list(addtl_args) + list(to_type.addtl_args) + ['-f', to_type.identifier, path]
            if from_format and from_format.list_all:

                files = sorted([os.path.join(temp_dir, f.name) for f in file_group],
                               partial(sort_by_extension_index, from_format))

                _ogr2ogr_cli(ogr2ogr_args + [','.join(files)], *args, **kwargs)
            else:
                _ogr2ogr_cli(ogr2ogr_args + [os.path.join(temp_dir, main_file.name)], *args, **kwargs)

        files = []
        if os.path.isdir(path):
            files = [os.path.join(path, name) for name in os.listdir(path)]
        elif os.path.exists(path):
            for filename in os.listdir(out_path):
                if os.path.splitext(filename)[0] == 'out':
                    # splitext returns extension *including* the dot
                    ext = '.' + to_type.extension[0] if filename == 'out' else os.path.splitext(filename)[1]

                    files.append(
                        os.path.join(out_path, '{}{}'.format(main_file.basename if main_file else 'out', ext)))
                    shutil.move(os.path.join(out_path, filename), files[-1])

        groups = collections.defaultdict(list)
        for file in files:
            groups[os.path.splitext(file)[0]].append(file)

        return [FileGroup.from_files(*f) for f in groups.values()]


def sort_by_extension_index(from_format, a, b):
    """
    Force main file(s) to appear a) first and b) in the order specified in the format
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

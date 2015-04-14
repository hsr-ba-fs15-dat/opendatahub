"""
ogr2ogr (GDAL) command line interface wrapper
Requires ogr2ogr to be installed (e.g. sudo apt-get install gdal-bin)
"""

import subprocess
import collections

import os
import shutil
import logging

from hub.structures.file import FileGroup


class Ogr2OgrException(Exception):
    pass


OgrFomat = collections.namedtuple('OgrFormat', ('extension', 'identifier', 'list_all'))

GML = OgrFomat('gml', 'GML', False)
SHP = OgrFomat('shp', 'ESRI Shapefile', False)
CSV = OgrFomat('csv', 'CSV', False)
GEO_JSON = OgrFomat('json', 'GeoJSON', False)
KML = OgrFomat('kml', 'KML', False)

# todo needs further research in how these two work, currently they fail, duh
INTERLIS_1 = OgrFomat('ili', 'Interlis 1', True)
# INTERLIS_2 = OgrFomat('ili', 'Interlis 2')


OGR_BY_EXTENSION = {}
for var in globals().values():
    if isinstance(var, OgrFomat):
        OGR_BY_EXTENSION[var.extension] = var


def _ogr2ogr_cli(arguments, *agrs, **kwargs):
    cmd = ['ogr2ogr'] + arguments
    logging.debug('Running ogr2ogr: %s', ' '.join(cmd))
    process = subprocess.Popen(cmd)
    exit_code = process.wait()
    if exit_code:
        raise Ogr2OgrException()


def ogr2ogr(file_group, to_type):
    main_file = next((f for f in file_group if f.extension in OGR_BY_EXTENSION))

    if OGR_BY_EXTENSION[main_file.extension] == to_type:
        return file_group

    with file_group.on_filesystem() as temp_dir:
        path = os.path.join(temp_dir, 'out')

        from_format = OGR_BY_EXTENSION.get(main_file.extension)
        if from_format and from_format.list_all:
            _ogr2ogr_cli(['-f', to_type.identifier, path, ','.join([os.path.join(temp_dir, f.name)
                                                                    for f in file_group])])
        else:
            _ogr2ogr_cli(['-f', to_type.identifier, path, os.path.join(temp_dir, main_file.name)])

        if os.path.isdir(path):
            files = [os.path.join(path, name) for name in os.listdir(path)]
        elif os.path.exists(path):
            files = []
            for filename in os.listdir(temp_dir):
                if os.path.splitext(filename)[0] == 'out':
                    ext = to_type.extension if filename == 'out' else filename.rsplit('.', 1)[-1]

                    files.append(os.path.join(temp_dir, '{}.{}'.format(main_file.basename, ext)))
                    shutil.move(os.path.join(temp_dir, filename), files[-1])

        groups = collections.defaultdict(list)
        for file in files:
            groups[os.path.splitext(file)[0]].append(file)

        return sorted([FileGroup.from_files(*f) for f in groups.values()], key=lambda fg: fg.get_main_file().name)

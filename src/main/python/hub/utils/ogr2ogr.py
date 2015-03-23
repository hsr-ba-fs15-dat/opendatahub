"""

"""

import subprocess
import collections

import os
import shutil

from hub.structures.file import FileGroup


class Ogr2OgrException(Exception):
    pass


OgrFomat = collections.namedtuple('OgrFormat', ('extension', 'identifier'))

GML = OgrFomat('gml', 'GML')
SHP = OgrFomat('shp', 'ESRI Shapefile')
CSV = OgrFomat('csv', 'CSV')
GEO_JSON = OgrFomat('json', 'GeoJSON')
KML = OgrFomat('kml', 'KML')

# todo needs further research in how these two work, currently they fail, duh
# INTERLIS_1 = OgrFomat('ili', 'Interlis 1')
# INTERLIS_2 = OgrFomat('ili', 'Interlis 2')


OGR_BY_EXTENSION = {}
for var in globals().values():
    if isinstance(var, OgrFomat):
        OGR_BY_EXTENSION[var.extension] = var


def _ogr2ogr_cli(arguments, *agrs, **kwargs):
    cmd = ['ogr2ogr'] + arguments
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
        _ogr2ogr_cli(['-f', to_type.identifier, path, os.path.join(temp_dir, main_file.name)])

        if os.path.isdir(path):
            files = [os.path.join(path, name) for name in os.listdir(path)]
        elif os.path.exists(path):
            files = []
            for filename in os.listdir(temp_dir):
                if os.path.splitext(filename)[0] == 'out':
                    ext = to_type.extension if filename == 'out' else filename.rsplit('.', 1)[-1]

                    files.append(os.path.join(temp_dir, '{}.{}'.format(os.path.splitext(main_file.name)[0], ext)))
                    shutil.move(os.path.join(temp_dir, filename), files[-1])

        file_group_converted = FileGroup.from_files(*files)
        # some ogr2ogr drivers don't retain the name (evil!), let's rename them ourselves
        for file in file_group_converted:
            file.name = os.path.splitext(main_file.name)[0] + os.path.splitext(file.name)[1]

        return file_group_converted

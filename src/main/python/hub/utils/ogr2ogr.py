"""

"""

import subprocess
import collections

import os

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
            files = [os.path.join(temp_dir, '{}.{}'.format(main_file.name.rsplit('.', 1)[0], to_type.extension))]
            os.rename(path, files[0])

        return FileGroup.from_files(*files)

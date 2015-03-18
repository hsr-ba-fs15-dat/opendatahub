"""

"""

import subprocess
from cStringIO import StringIO
import shutil
import tempfile

import os


class Ogr2OgrException(Exception):
    pass


OGR2OGR_FILES = {
    # file extension -> type in ogr2ogr
    '.gml': 'GML',
    '.shp': 'ESRI Shapefile',
    # todo more to come
}


def _ogr2ogr_cli(arguments, *agrs, **kwargs):
    cmd = ['ogr2ogr'] + arguments
    process = subprocess.Popen(cmd)
    exit_code = process.wait()
    if exit_code:
        raise Ogr2OgrException()


def ogr2ogr(from_files, to_type):
    main_file = next((name for name in from_files.keys() if os.path.splitext(name)[1] in OGR2OGR_FILES))

    if OGR2OGR_FILES[os.path.splitext(main_file)[1]] == to_type:
        return from_files

    temp_dir = tempfile.mkdtemp('ogr2ogr')
    try:
        for from_file_name, from_file_stream in from_files.iteritems():
            with open(os.path.join(temp_dir, from_file_name), 'wb') as f:
                f.write(from_file_stream.getvalue())

        path = os.path.join(temp_dir, 'temp')
        _ogr2ogr_cli(['-f', to_type, path, os.path.join(temp_dir, main_file)])

        out_files = {}
        for file_name in os.listdir(path):
            abs_path = os.path.join(path, file_name)
            with open(abs_path, 'rb') as f:
                out_files[file_name] = StringIO(''.join(f.readlines()))

        return out_files

    finally:
        shutil.rmtree(temp_dir)

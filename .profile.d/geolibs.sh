#!/usr/bin/env bash

export GEOS_LIBRARY_PATH="/app/.geodjango/geos/lib/libgeos_c.so"
export GDAL_LIBRARY_PATH="/app/.geodjango/gdal/lib/libgdal.so"

export CPPPATH="$CPPPATH:/app/.geodjango/gdal/include"
export CPATH="$CPATH:/app/.geodjango/gdal/include"
export LIBRARY_PATH="$LIBRARY_PATH:/app/.geodjango/gdal/lib"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/app/.geodjango/gdal/lib:/app/.geodjango/geos/lib"
export PATH="$PATH:/app/.geodjango/gdal/bin"

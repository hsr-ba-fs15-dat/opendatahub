# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Geometry functions. Functions and naming borrowed from PostGIS.
"""

from shapely import wkt

import geopandas as gp
import pyproj
from fiona.crs import from_epsg
import numpy as np

from hub.odhql.functions.core import VectorizedFunction, OdhQLExecutionException


class VectorizedGeometryFunction(VectorizedFunction):
    _is_abstract = True

    def apply(self, *args):
        super(VectorizedGeometryFunction, self).apply(*args)

    def get_crs(self, epsg):
        self.assert_int('srid', epsg)
        crs = from_epsg(epsg)
        try:
            pyproj.Proj(**crs)
        except RuntimeError:
            raise OdhQLExecutionException('{}: Unknown SRID "{}"'.format(self.name, epsg))
        return crs


class GeomFromText(VectorizedGeometryFunction):
    name = 'ST_GeomFromText'

    def apply(self, wkts):
        wkts = self.expand(wkts)
        # todo figure better assertions
        self.assert_str('wkt', wkts)
        try:
            return gp.GeoSeries([wkt.loads(text) for text in wkts])
        except Exception as e:
            raise OdhQLExecutionException('Error loading WKT "{}": "{}"'.format(text, e.message))


class SetSRID(VectorizedGeometryFunction):
    name = 'ST_SetSRID'

    def apply(self, geoms, srid):
        self.assert_geometry('geometry', geoms)
        self.assert_int('srid', srid)
        geoms.crs = self.get_crs(srid)
        return geoms


class SRID(VectorizedGeometryFunction):
    name = 'ST_SRID'

    def apply(self, geoms):
        self.assert_geometry('geometry', geoms)
        srid = np.nan
        if geoms.crs:
            try:
                srid = int(geoms.crs['init'].split(':')[-1])
            except KeyError:
                srid = pyproj.Proj(geoms.crs).srs
        return self.expand(srid)


class AsText(VectorizedGeometryFunction):
    name = 'ST_AsText'

    def apply(self, geoms):
        self.assert_geometry('geometry', geoms)
        return geoms.astype(str)


class Centroid(VectorizedGeometryFunction):
    name = 'ST_Centroid'

    def apply(self, geoms):
        self.assert_geometry('geometry', geoms)
        return gp.GeoSeries(geoms).centroid


class GetX(VectorizedGeometryFunction):
    name = 'ST_X'

    def apply(self, geoms):
        self.assert_geometry('geometry', geoms)
        return gp.GeoSeries(geoms).bounds.minx


class GetY(VectorizedGeometryFunction):
    name = 'ST_Y'

    def apply(self, geoms):
        self.assert_geometry('geometry', geoms)
        return gp.GeoSeries(geoms).bounds.miny


class Area(VectorizedGeometryFunction):
    """
    Area in square feet
    """
    name = 'ST_Area'

    def apply(self, geoms):
        self.assert_geometry('geometry', geoms)
        return gp.GeoSeries(geoms).area

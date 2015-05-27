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
    """
    Erstellt eine Spalte mit Geometrie-Objekten aus einem Well-Known-Text (WKT).

    Parameter
        - `wkts`: Spalte oder Wert mit WKTs.
        - `srid`: Optional die SRID der Geometrien.

    Siehe auch: `PostGIS ST_GeomFromText <http://postgis.net/docs/ST_GeomFromText.html>`_

    Beispiel
        .. code:: sql

            ST_GeomFromText(\'POINT(7.2234283 48.8183157)\', 4326) AS hsr
    """
    name = 'ST_GeomFromText'

    def apply(self, wkts, srid=None):
        wkts = self.expand(wkts)
        self.assert_str('wkt', wkts)
        crs = self.get_crs(srid) if srid else {}
        try:
            return gp.GeoSeries([wkt.loads(text) for text in wkts], crs=crs)
        except Exception as e:
            raise OdhQLExecutionException('Error loading WKT "{}": "{}"'.format(text, e.message))


class SetSRID(VectorizedGeometryFunction):
    """
    Setzt das Koordinatensystem (Spatial Reference Identifier, kurz SRID) einer Geometrie-Spalte.

    Parameter
        - `geoms`: Spalte mit Geometrien.
        - `srid`: SRID der Geometrien.

    Siehe auch: `PostGIS ST_SetSRID <http://postgis.net/docs/ST_SetSRID.html>`_

    Beispiel
        .. code:: sql

            ST_SetSRID(ODH12.latlng, 4326) AS geometry
    """
    name = 'ST_SetSRID'

    def apply(self, geoms, srid):
        self.assert_geometry('geoms', geoms)
        geoms.crs = self.get_crs(srid)
        return geoms


class SRID(VectorizedGeometryFunction):
    """
    Liefert das Koordinatensystem einer Geometrie-Spalte. Sollte keine Identifikationsnummer (SRID) bekannt sein, so
    wird eine Zeichenkette mit den Projektionsparametern im PROJ.4 <http://trac.osgeo.org/proj/>`_ Format
    zurückgegeben.

    Parameter
        - `geoms`: Spalte mit Geometrien.

    Siehe auch: `PostGIS ST_SRID <http://postgis.net/docs/ST_SRID.html>`_

    Beispiel
        .. code:: sql

            ST_SRID(ODH12.latlng) AS srid
    """

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
    """
    Liefert die Geometrien als Well-Known-Text (WKT) Zeichenkette,

    Parameter
        - `geoms`: Spalte mit Geometrien.

    Siehe auch: `PostGIS ST_AsText <http://postgis.net/docs/ST_AsText.html>`_

    Beispiel
        .. code:: sql

            ST_AsText(ODH12.geometry) AS wkt
    """
    name = 'ST_AsText'

    def apply(self, geoms):
        self.assert_geometry('geometry', geoms)
        return geoms.astype(str)


class Centroid(VectorizedGeometryFunction):
    """
    Berechnet den Mittelpunkt der Geometrien.

    Parameter
        - `geoms`: Spalte mit Geometrien.

    Siehe auch: `PostGIS ST_Centroid <http://postgis.net/docs/ST_Centroid.html>`_

    Beispiel
        .. code:: sql

            ST_Centroid(ODH12.geometry) AS point
    """
    name = 'ST_Centroid'

    def apply(self, geoms):
        self.assert_geometry('geometry', geoms)
        return geoms.geom_op('centroid')


class GetX(VectorizedGeometryFunction):
    """
    Liefert die kleinste X-Komponente der Geometrien.
    **Achtung:** Funktioniert aus diesem Grund anders wie in PostGIS nicht nur mit Punkten.

    Parameter
        - `geoms`: Spalte mit Geometrien.

    Siehe auch: `PostGIS ST_X <http://postgis.net/docs/ST_X.html>`_

    Beispiel
        .. code:: sql

            ST_X(ODH12.latlng) AS x
    """
    name = 'ST_X'

    def apply(self, geoms):
        self.assert_geometry('geometry', geoms)
        return geoms.geom_op('bounds').minx


class GetY(VectorizedGeometryFunction):
    """
    Liefert die kleinste Y-Komponente der Geometrien.
    **Achtung:** Funktioniert aus diesem Grund anders wie in PostGIS nicht nur mit Punkten.

    Parameter
        - `geoms`: Spalte mit Geometrien.

    Siehe auch: `PostGIS ST_Y <http://postgis.net/docs/ST_Y.html>`_

    Beispiel
        .. code:: sql

            ST_Y(ODH12.latlng) AS y
    """
    name = 'ST_Y'

    def apply(self, geoms):
        self.assert_geometry('geometry', geoms)
        return geoms.geom_op('bounds').miny


class Area(VectorizedGeometryFunction):
    """
    Berechnet die Fläche der Geometrien in der Einheit des Koordinatensystems.

    Parameter
        - `geoms`: Spalte mit Geometrien.

    Siehe auch: `PostGIS ST_Area <http://postgis.net/docs/ST_Area.html>`_

    Beispiel
        .. code:: sql

            ST_X(ODH12.geometry) AS area
    """
    name = 'ST_Area'

    def apply(self, geoms):
        self.assert_geometry('geometry', geoms)
        return geoms.geom_op('area')


class Transform(VectorizedGeometryFunction):
    """
    Transformiert die Geometrien in ein anderes Koordinatensystem. Auf den Geometrien muss bereits eine SRID gesetzt
    sein.

    Parameter
        - `geoms`: Spalte mit Geometrien.
        - `srid`: SRID der Geometrien.

    Siehe auch: `PostGIS ST_Transform <http://postgis.net/docs/ST_Transform.html>`_

    Beispiel
        .. code:: sql

            ST_Transform(ODH12.mercator, 4326) AS latlng
    """
    name = 'ST_Transform'

    def apply(self, geoms, srid):
        self.assert_geometry('geoms', geoms)
        crs = self.get_crs(srid)
        with self.errorhandler():
            return geoms.geom_op('to_crs', crs)

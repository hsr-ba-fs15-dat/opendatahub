"""
Geometry functions. Functions and naming borrowed from PostGIS.
"""

from shapely import wkt

import geopandas as gp
from fiona import crs
import numpy as np

from hub.odhql.functions.core import VectorizedFunction, OdhQLExecutionException


class GeomFromText(VectorizedFunction):
    name = 'ST_GeomFromText'

    def apply(self, wkts):
        wkts = self.expand(wkts)
        # todo figure better assertions
        self.assert_str('wkt', wkts[0])
        try:
            return gp.GeoSeries([wkt.loads(text) for text in wkts])
        except Exception as e:
            raise OdhQLExecutionException('Error loading WKT "{}": "{}"'.format(text, e.message))


class SetSRID(VectorizedFunction):
    name = 'ST_SetSRID'

    def apply(self, geoms, srid):
        # todo assert geom
        # todo assert srid
        self.assert_int('srid', srid)
        geoms.crs = crs.from_epsg(srid)
        return geoms


class SRID(VectorizedFunction):
    name = 'ST_SRID'

    def apply(self, geoms):
        # todo assert geom
        srid = np.nan
        if geoms.crs:
            srid = int(geoms.crs['init'].split(':')[-1])
        return self.expand(srid)


class AsText(VectorizedFunction):
    name = 'ST_AsText'

    def apply(self, geoms):
        # todo assert geom
        return geoms.astype(str)

from __future__ import unicode_literals

"""
Tests for OdhQL functions.
Are compared to python equivalents ("known" to operate correctly) instead of fixed/floored values.
"""

import traceback
import logging

import pandas as pd

from hub.tests.tests_interpreter import TestInterpreterBase
from hub.odhql.exceptions import OdhQLExecutionException


class TestStringFunctions(TestInterpreterBase):
    def test_concat(self):
        df = self.execute('SELECT e.prename, e.surname, CONCAT(e.prename, \' \', e.surname) AS fullname '
                          'FROM employee AS e')
        self.assertListEqual(df.fullname.tolist(), [s.prename + ' ' + s.surname for i, s in df.iterrows()])

    def test_trim(self):
        df = self.execute('SELECT TRIM(e.prename) as prename, TRIM(e.surname) as surname FROM employee AS e')
        self.assertFalse(any([s.startswith(' ') or s.endswith(' ') for s in df.prename.tolist() + df.surname.tolist()]))

    def test_ltrim(self):
        df = self.execute('SELECT LTRIM(e.prename) as prename, TRIM(e.surname) as surname FROM employee AS e')
        self.assertFalse(any([s.startswith(' ') for s in df.prename.tolist() + df.surname.tolist()]))

    def test_rtrim(self):
        df = self.execute('SELECT RTRIM(e.prename) as prename, TRIM(e.surname) as surname FROM employee AS e')
        self.assertFalse(any([s.endswith(' ') for s in df.prename.tolist() + df.surname.tolist()]))

    def test_upper(self):
        df = self.execute('SELECT UPPER(e.prename) as prename FROM employee AS e')
        self.assertListEqual(df.prename.tolist(), [n.upper() for n in self.employees.Prename.tolist()])

    def test_lower(self):
        df = self.execute('SELECT LOWER(e.prename) as prename FROM employee AS e')
        self.assertListEqual(df.prename.tolist(), [n.lower() for n in self.employees.Prename.tolist()])

    def test_len(self):
        df = self.execute('SELECT LEN(e.prename) as lens FROM employee AS e')
        self.assertListEqual(df.lens.tolist(), [len(n) for n in self.employees.Prename.tolist()])

    def test_extract(self):
        df = self.execute('SELECT EXTRACT(e.prename, \'(Ann)\') as extracted FROM employee AS e')
        self.assertSetEqual({'Ann'}, set(df.extracted[~pd.isnull(df.extracted)].tolist()))

    def test_startswith(self):
        df = self.execute('SELECT STARTSWITH(e.prename, \'Ann\') as starts_ann FROM employee AS e')
        self.assertListEqual(df.starts_ann.tolist(), [n.startswith('Ann') for n in self.employees.Prename.tolist()])

    def test_endswith(self):
        df = self.execute('SELECT ENDSWITH(e.prename, \'er\') as ends_er FROM employee AS e')
        self.assertListEqual(df.ends_er.tolist(), [n.endswith('er') for n in self.employees.Prename.tolist()])

    def test_get(self):
        df = self.execute('SELECT GET(e.prename, 0) as first_letter FROM employee AS e')
        self.assertListEqual(df.first_letter.tolist(), [n[0] for n in self.employees.Prename.tolist()])

    def test_contains(self):
        df = self.execute('SELECT CONTAINS(e.prename, \'ann\', True) as contains_ann FROM employee AS e')
        self.assertNotIn(True, df.contains_ann.tolist())

        df = self.execute('SELECT CONTAINS(e.prename, \'ann\', False) as contains_ann FROM employee AS e')
        self.assertListEqual(df.contains_ann.tolist(), ['ann' in n.lower() for n in self.employees.Prename.tolist()])

    def test_replace(self):
        df = self.execute('SELECT REPLACE(e.prename, \'ann\', \'ANN\', False) as replaced FROM employee AS e')
        self.assertTrue(all(['ANN' in n for n in df.replaced.tolist() if 'ann' in n.lower()]))

    def test_repeat(self):
        df = self.execute('SELECT REPEAT(e.prename, 4) as repeated FROM employee AS e')
        self.assertListEqual(df.repeated.tolist(), [4 * n for n in self.employees.Prename.tolist()])

    def test_pad_left(self):
        df = self.execute('SELECT PAD(e.prename, 20, \'left\') as padded FROM employee AS e')
        self.assertListEqual(df.padded.tolist(), [(' ' * (20 - len(n))) + n for n in self.employees.Prename.tolist()])

    def test_count(self):
        df = self.execute('SELECT COUNT(e.prename, \'i\') as occurrences FROM employee AS e')
        self.assertListEqual(df.occurrences.tolist(), [n.count('i') for n in self.employees.Prename.tolist()])

    def test_substring(self):
        df = self.execute('SELECT SUBSTRING(e.prename, 0, 2) as subs FROM employee AS e')
        self.assertListEqual(df.subs.tolist(), [n[0:2] for n in self.employees.Prename.tolist()])

    def test_fails(self):
        statements = (
            'SELECT CONCAT(1, 2) AS test FROM employee AS e',
            'SELECT CONCAT(c.prename, c.age) AS test FROM child AS c',
            'SELECT TRIM(c.age) AS test FROM child AS c',
            'SELECT LTRIM(c.age) AS test FROM child AS c',
            'SELECT RTRIM(c.age) AS test FROM child AS c',
            'SELECT UPPER(c.age) AS test FROM child AS c',
            'SELECT LOWER(c.age) AS test FROM child AS c',
            'SELECT LEN(c.age) AS test FROM child AS c',
            'SELECT EXTRACT(c.age, \'(Ann)\') AS test FROM child AS c',
            'SELECT EXTRACT(c.prename, \'(Ann\') AS test FROM child AS c',
            'SELECT EXTRACT(c.prename, \'Ann\') AS test FROM child AS c',
            'SELECT STARTSWITH(c.prename, c.age) AS test FROM child AS c',
            'SELECT STARTSWITH(c.age, \'Ann\') AS test FROM child AS c',
            'SELECT ENDSWITH(c.prename, c.age) AS test FROM child AS c',
            'SELECT ENDSWITH(c.age, \'Ann\') AS test FROM child AS c',
            'SELECT CONTAINS(c.prename, 4, True) AS test FROM child AS c',
            'SELECT CONTAINS(c.prename, \'str\', 4) AS test FROM child AS c',
            'SELECT REPLACE(c.prename, \'str\', 4) AS test FROM child AS c',
            'SELECT REPLACE(c.prename, 4, \'str\') AS test FROM child AS c',
            'SELECT REPLACE(c.age, \'str\', \'other\') AS test FROM child AS c',
            'SELECT REPEAT(c.age, 4) AS test FROM child AS c',
            'SELECT REPEAT(c.prename, \'str\') AS test FROM child AS c',
            'SELECT PAD(c.prename, 20, \'some_side\') AS test FROM child AS c',
            'SELECT PAD(c.age, 20, \'left\') AS test FROM child AS c',
            'SELECT PAD(c.prename, \'str\', \'left\') AS test FROM child AS c',
            'SELECT COUNT(c.age, \'i\') AS test FROM child AS c',
            'SELECT COUNT(c.prename, 4) AS test FROM child AS c',
            'SELECT SUBSTRING(c.prename, 4, \'a\') AS test FROM child AS c',
            'SELECT SUBSTRING(c.prename, \'a\', 4) AS test FROM child AS c',
            'SELECT SUBSTRING(c.age, 0, 4) AS test FROM child AS c',
        )

        for statement in statements:
            self.assertRaises(OdhQLExecutionException, lambda: self.execute(statement))


class TestMiscFunctions(TestInterpreterBase):
    def test_cast_int_to_str(self):
        df = self.execute('SELECT CAST(c.age, \'TEXT\') AS age FROM child AS c')
        self.assertIsInstance(df.age[0], basestring)

    def test_cast_str_to_float(self):
        df = self.execute('SELECT CAST(\'3.141\', \'FLOAT\') AS age FROM child AS c')
        self.assertListEqual([3.141] * len(df), df.age.tolist())

    def test_cast_str_to_int(self):
        df = self.execute('SELECT CAST(\'3.141\', \'INTEGER\') AS age FROM child AS c')
        self.assertListEqual([3] * len(df), df.age.tolist())

    def test_parse_datetime(self):
        df = self.execute('SELECT PARSE_DATETIME(\'1990-10-13\') AS bday FROM child AS c')
        bday = df.bday[0]
        self.assertListEqual([bday.day, bday.month, bday.year], [13, 10, 1990])  # yes, my bday!

    def test_cast_int_to_datetime(self):
        df = self.execute('SELECT CAST(655776000, \'DATETIME\') AS bday FROM child AS c')
        self.assertEqual(str(df.bday[0]), '1990-10-13 00:00:00')  # yes, my bday!

    def test_nvl(self):
        self.execute('SELECT NVL(c.age, c.id) AS with_col, NVL(c.age, \'no age\') AS with_literal FROM child AS c')

    def test_fails(self):
        statements = (
            'SELECT CAST(e.surname, \'foobar\') AS test FROM employee AS e',
            'SELECT CAST(\'1990-10-13\', \'DATETIME\') AS age FROM child AS c',
        )

        for statement in statements:
            self.assertRaises(OdhQLExecutionException, lambda: self.execute(statement))


class TestGeometryFunctions(TestInterpreterBase):
    def test_geom_from_text(self):
        self.execute('SELECT c.prename, ST_GeomFromText(\'POINT(4 6)\') AS blabla FROM child AS c')

    def test_set_srid(self):
        df = self.execute('SELECT c.prename, ST_SetSRID(ST_GeomFromText(\'POINT(7.2234283 48.8183157)\'), 4326) AS hsr '
                          'FROM child AS c')
        self.assertTrue(df.hsr.crs['init'], 'epsg:4326')

    def test_srid(self):
        self.execute('SELECT c.prename, '
                     'ST_SRID(ST_SetSRID(ST_GeomFromText(\'POINT(7.2234283 48.8183157)\'), 4326)) AS hsr '
                     'FROM child AS c')

    def test_astext(self):
        self.execute('SELECT c.prename, ST_AsText(ST_GeomFromText(\'POINT(7.2234283 48.8183157)\')) AS hsr '
                     'FROM child AS c')

    def test_union(self):
        self.execute('SELECT ST_SetSRID(ST_GeomFromText(\'POINT(7.2234283 48.8183157)\'), 4326) AS hsr '
                     'FROM child AS c UNION '
                     'SELECT ST_SetSRID(ST_GeomFromText(\'POINT(804108.360138 6244089.40913)\'), 3857) AS hsr '
                     'FROM child AS c'
                     )
        # todo assert

    def test_st_x(self):
        df = self.execute('SELECT c.prename, ST_X(ST_GeomFromText(\'POINT(7.2234283 48.8183157)\')) AS hsrx '
                          'FROM child AS c')
        self.assertListEqual(len(df) * [7.2234283], df.hsrx.tolist())

    def test_st_y(self):
        df = self.execute('SELECT c.prename, ST_Y(ST_GeomFromText(\'POINT(7.2234283 48.8183157)\')) AS hsry '
                          'FROM child AS c')
        self.assertListEqual(len(df) * [48.8183157], df.hsry.tolist())

    def test_st_area_point(self):
        df = self.execute('SELECT c.prename, ST_Area(ST_GeomFromText(\'POINT(7.2234283 48.8183157)\')) AS area '
                          'FROM child AS c')
        self.assertListEqual(len(df) * [0], df['area'].tolist())

    def test_st_area_poly(self):
        # polygon & result from http://postgis.net/docs/ST_Area.html
        df = self.execute('SELECT c.prename, ST_Area(ST_SetSRID(ST_GeomFromText(\'POLYGON((743238 2967416,743238 '
                          '2967450,743265 2967450,743265.625 2967416,743238 2967416))\'), 2249)) AS area '
                          'FROM child AS c')
        self.assertListEqual(len(df) * [928.625], df['area'].tolist())

    def test_fails(self):
        statements = (
            ('SELECT c.prename, ST_SetSRID(ST_GeomFromText(\'POINT(7.2234283 48.8183157)\'), 99999) AS hsr '
             'FROM child AS c', 'Unknown SRID'),

            # todo different/no crs
        )

        for statement, message in statements:
            try:
                self.assertRaises(OdhQLExecutionException, lambda: self.execute(statement))
            except:
                logging.info(traceback.format_exc())
                self.fail(message)

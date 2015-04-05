# -*- coding: utf-8 -*-
"""
Tests for OdhQL functions.
Are compared to python equivalents ("known" to operate correctly) instead of fixed/floored values.
"""

import pandas as pd

from hub.tests.tests_interpreter import TestInterpreterBase, CHILDREN_CSV, EMPLOYEES_CSV
from hub.structures.file import File
from hub.odhql.exceptions import OdhQLExecutionException


class TestStringFunctions(TestInterpreterBase):
    def setUp(self):
        self.employees = File.from_string('employees.csv', EMPLOYEES_CSV).to_df()
        self.children = File.from_string('children.csv', CHILDREN_CSV).to_df()
        super(TestStringFunctions, self).setUp()

    def get_source_dfs(self):
        return {
            'employee': self.employees,
            'child': self.children
        }

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
    def setUp(self):
        self.employees = File.from_string('employees.csv', EMPLOYEES_CSV).to_df()
        self.children = File.from_string('children.csv', CHILDREN_CSV).to_df()
        super(TestMiscFunctions, self).setUp()

    def get_source_dfs(self):
        return {
            'employee': self.employees,
            'child': self.children
        }

    def test_cast_int_to_str(self):
        df = self.execute('SELECT CAST(c.age, \'str\') AS age FROM child AS c')
        self.assertIsInstance(df.age[0], basestring)

    def test_nvl(self):
        self.execute('SELECT NVL(c.age, c.id) AS with_col, NVL(c.age, \'no age\') AS with_literal FROM child AS c')

    def test_fails(self):
        statements = (
            'SELECT CAST(e.surname, \'foobar\') AS test FROM employee AS e',

        )

        for statement in statements:
            self.assertRaises(OdhQLExecutionException, lambda: self.execute(statement))


class TestGeometryFunctions(TestInterpreterBase):
    def setUp(self):
        self.employees = File.from_string('employees.csv', EMPLOYEES_CSV).to_df()
        self.children = File.from_string('children.csv', CHILDREN_CSV).to_df()
        super(TestGeometryFunctions, self).setUp()

    def get_source_dfs(self):
        return {
            'employee': self.employees,
            'child': self.children
        }

    def test_geom_from_text(self):
        self.execute('SELECT c.prename, ST_GeomFromText(\'POINT(4 6)\') as blabla FROM child AS c')

    def test_set_srid(self):
        df = self.execute('SELECT c.prename, ST_SetSRID(ST_GeomFromText(\'POINT(48.8183157 7.2234283)\'), 4326) as hsr '
                          'FROM child AS c')
        self.assertTrue(df.crs['init'], 'epsg:4326')

    def test_srid(self):
        self.execute('SELECT c.prename, '
                     'ST_SRID(ST_SetSRID(ST_GeomFromText(\'POINT(48.8183157 7.2234283)\'), 4326)) as hsr '
                     'FROM child AS c')

    def test_astext(self):
        self.execute('SELECT c.prename, ST_AsText(ST_GeomFromText(\'POINT(48.8183157 7.2234283)\')) as hsr '
                     'FROM child AS c')

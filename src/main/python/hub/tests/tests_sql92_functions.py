# -*- coding: utf-8 -*-


from hub.tests.tests_interpreter import TestInterpreterBase, CHILDREN_CSV, EMPLOYEES_CSV
from hub.structures.file import File
from hub.odhql.exceptions import OdhQLExecutionException
import pandas as pd


class TestInterpreter(TestInterpreterBase):
    def setUp(self):
        self.employees = File.from_string('employees.csv', EMPLOYEES_CSV).to_df()
        self.children = File.from_string('children.csv', CHILDREN_CSV).to_df()
        super(TestInterpreter, self).setUp()

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
        self.execute('SELECT REPLACE(e.prename, \'ann\', \'ANN\', False) as replaced FROM employee AS e')

    def test_cast_int_to_str(self):
        df = self.execute('SELECT CAST(c.age, \'str\') AS age FROM child AS c')
        self.assertIsInstance(df.age[0], basestring)

    def test_cast_unknown_param(self):
        self.assertRaises(OdhQLExecutionException,
                          lambda: self.execute('SELECT CAST(e.surname, \'foobar\') AS test FROM employee AS e'))

    def test_nvl(self):
        self.execute('SELECT NVL(c.age, c.id) AS with_col, NVL(c.age, \'no age\') AS with_literal FROM child AS c')

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
        )

        for statement in statements:
            self.assertRaises(OdhQLExecutionException, lambda: self.execute(statement))

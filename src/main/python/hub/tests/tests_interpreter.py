# -*- coding: utf-8 -*-


import pandas as pd

from hub.tests.testutils import TestBase
from hub.structures.file import File
from hub.odhql.parser import OdhQLParser
from hub.odhql.interpreter import OdhQLInterpreter
import logging


EMPLOYEES_CSV = """
Id,Prename,Surname,Boss
0,Dieter ,Holzmann,
1, Lukas,Boehm,0
2, Eric ,Koertig,0
3,Markus,Schäfer,0
4,Anna,Oster,1
5,Christina,Peters,1
6,Annett,Neustadt,4
7,Ines,Baum,2
8,Robert,Aachen,7
9,Philipp,Baumgartner,5
"""

CHILDREN_CSV = """
Id,Parent,Prename,Surname,Age
0,0,Katrin,Holzmann,6
1,0,Mike,Holzmann,13
2,6,Andrea,Neustadt,19
3,9,Lisa,Baumgartner,22
4,2,Matthias,Koertig,25
5,2,Karolin,Koertig,
6,4,Sabrina,Oster,32
7,7,Melanie,Baum,17
8,8,Marko,Aachen,3
9,1,Annett,Boehm,2
"""


class TestInterpreterBase(TestBase):
    def setUp(self):
        self.source_dfs = self.get_source_dfs()

        self.parser = OdhQLParser()
        self.interpreter = OdhQLInterpreter(self.source_dfs)

    def get_source_dfs(self):
        raise NotImplementedError

    def execute(self, query):
        logging.info('Executing query "%s"', query)
        df = self.interpreter.execute(query)
        logging.info('Query result: %s', df)
        return df


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

    def test_select(self):
        df = self.execute('SELECT employee.Id, employee.Prename FROM employee')
        self.assertListEqual(df.columns.tolist(), ['Id', 'Prename'])

    def test_select_caseless(self):
        df = self.execute('SELECT Employee.id, employeE.preName FROM EmPlOyEe')
        self.assertListEqual(df.columns.tolist(), ['id', 'preName'])

    def test_alias(self):
        df = self.execute('SELECT e.id, E.surname FROM employee AS e')
        self.assertListEqual(df.columns.tolist(), ['id', 'surname'])

    def test_where_int_equal(self):
        df = self.execute('SELECT c.age FROM child AS c WHERE c.age = 19')
        self.assertListEqual([19] * len(df), df.age.tolist())

    def test_where_int_not_equal(self):
        df = self.execute('SELECT c.age FROM child AS c WHERE c.age != 19')
        self.assertNotIn(19, df.age)

    def test_where_int_greater(self):
        df = self.execute('SELECT c.age FROM child AS c WHERE c.age > 25')
        self.assertGreater(df.age.min(), 25)

    def test_where_int_greater_equal(self):
        df = self.execute('SELECT c.age FROM child AS c WHERE c.age >= 25')
        self.assertGreaterEqual(df.age.min(), 25)

    def test_where_int_less(self):
        df = self.execute('SELECT c.age FROM child AS c WHERE c.age < 3')
        self.assertLess(df.age.max(), 3)

    def test_where_int_less_equal(self):
        df = self.execute('SELECT c.age FROM child AS c WHERE c.age <= 3')
        self.assertLessEqual(df.age.max(), 3)

    def test_where_string_equal(self):
        df = self.execute('SELECT c.surname FROM child AS c WHERE c.surname = \'Holzmann\'')
        self.assertListEqual(['Holzmann'] * len(df), df.surname.tolist())

    def test_where_string_not_equal(self):
        df = self.execute('SELECT c.surname FROM child AS c WHERE c.surname != \'Holzmann\'')
        self.assertNotIn('Holzmann', df.surname.tolist())

    def test_where_or(self):
        df = self.execute('SELECT c.surname, c.age FROM child AS c WHERE c.surname = \'Holzmann\' OR c.age = 3')
        self.assertIn('Holzmann', df.surname.tolist())
        self.assertIn(3, df.age.tolist())

    def test_where_and(self):
        df = self.execute('SELECT c.surname, c.age FROM child AS c WHERE c.surname = \'Holzmann\' AND c.age = 6')
        self.assertListEqual(['Holzmann'] * len(df), df.surname.tolist())
        self.assertListEqual([6] * len(df), df.age.tolist())

    def test_where_null(self):
        df = self.execute('SELECT c.age FROM child AS c WHERE c.age IS NULL')
        self.assertTrue(pd.isnull(df.age).all())

    def test_where_not_null(self):
        df = self.execute('SELECT c.age FROM child AS c WHERE c.age IS NOT NULL')
        self.assertFalse(pd.isnull(df.age).any())

    def test_where_in(self):
        df = self.execute('SELECT c.surname FROM child as c WHERE c.surname IN (\'Holzmann\', \'Oster\')')
        self.assertIn('Holzmann', df.surname.tolist())
        self.assertIn('Oster', df.surname.tolist())
        self.assertEqual(len(set(df.surname.tolist())), 2)

    def test_where_not_in(self):
        df = self.execute('SELECT c.surname FROM child as c WHERE c.surname NOT IN (\'Holzmann\', \'Oster\')')
        self.assertNotIn('Holzmann', df.surname.tolist())
        self.assertNotIn('Oster', df.surname.tolist())

    def test_join(self):
        df = self.execute('SELECT c.prename, e.prename AS parent FROM child AS c JOIN employee AS e ON c.parent = e.id')
        self.assertEqual(len(df), len(self.children))

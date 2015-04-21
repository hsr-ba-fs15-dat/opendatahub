# -*- coding: utf-8 -*-


import logging
import traceback
import time

import pandas as pd

from hub.odhql.exceptions import OdhQLExecutionException
from hub.tests.testutils import TestBase
from hub.structures.file import File
from hub.odhql.parser import OdhQLParser
from hub.odhql.interpreter import OdhQLInterpreter


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
    @classmethod
    def setUpClass(cls):
        cls.read_data()

    @classmethod
    def tearDownClass(cls):
        cls.employees = None
        cls.children = None
        cls.source_dfs = None

    @classmethod
    def get_source_dfs(cls):
        return cls.source_dfs

    @classmethod
    def read_data(cls):
        cls.employees = File.from_string('employees.csv', EMPLOYEES_CSV).to_df()[0]
        cls.children = File.from_string('children.csv', CHILDREN_CSV).to_df()[0]
        cls.source_dfs = {
            'employee': cls.employees,
            'child': cls.children
        }

    def setUp(self):
        self.parser = OdhQLParser()
        self.interpreter = OdhQLInterpreter(self.get_source_dfs())

    def execute(self, query):
        logging.info('Executing query "%s"', query)
        t0 = time.time()
        df = self.interpreter.execute(query)
        self.time = round(time.time() - t0, 2)
        logging.info('Query result: %s', df)
        logging.info('"{}" took {}s.'.format(query, self.time))
        return df


class TestInterpreter(TestInterpreterBase):
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

    def test_where_like(self):
        df = self.execute('SELECT c.surname FROM child as c WHERE c.surname LIKE \'^H.*\'')
        self.assertNotIn(False, [s.startswith('H') for s in df.surname])

    def test_where_not_like(self):
        df = self.execute('SELECT c.surname FROM child as c WHERE c.surname NOT LIKE \'^H.*\'')
        self.assertNotIn(False, [not s.startswith('H') for s in df.surname])

    def test_join(self):
        df = self.execute('SELECT c.prename, e.prename AS parent FROM child AS c JOIN employee AS e ON c.parent = e.id')
        self.assertEqual(len(df), len(self.children))

    def test_self_join(self):
        df = self.execute('SELECT e.prename, ee.prename AS boss '
                          'FROM employee AS e JOIN employee AS ee ON e.boss = ee.id')
        self.assertListEqual(
            [self.employees.iloc[e.Boss].Prename for i, e in self.employees.iterrows() if not pd.isnull(e.Boss)],
            df.boss.tolist())

    def test_multi_join(self):
        self.execute('SELECT e.prename, ee.prename AS boss, c.prename AS childname, bc.prename AS bosses_child '
                     'FROM employee AS e '
                     'JOIN employee AS ee ON e.boss = ee.id '
                     'JOIN child AS c ON c.parent = e.id '
                     'JOIN child AS bc ON bc.parent = e.boss')

    def test_multicondition_join(self):
        df = self.execute(
            'SELECT c.prename, e.prename AS parent FROM child AS c JOIN employee AS e ON (c.parent = e.id '
            'AND e.id = c.parent)')
        self.assertEqual(len(df), len(self.children))

    def test_union(self):
        df = self.execute('SELECT e.prename FROM employee AS e UNION SELECT c.prename FROM child AS c')
        self.assertListEqual(df.prename.tolist(),
            [p for p in self.employees.Prename.tolist() + self.children.Prename.tolist()])

    def test_order_desc(self):
        df = self.execute('SELECT e.prename FROM employee AS e ORDER BY e.prename DESC')
        self.assertListEqual(df.prename.tolist(), sorted(self.employees.Prename.tolist())[::-1])

    def test_order_asc(self):
        df = self.execute('SELECT e.prename FROM employee AS e ORDER BY e.prename ASC')
        self.assertListEqual(df.prename.tolist(), sorted(self.employees.Prename.tolist()))

    def test_order_positional(self):
        df = self.execute('SELECT e.prename FROM employee AS e ORDER BY 1 ASC')
        self.assertListEqual(df.prename.tolist(), sorted(self.employees.Prename.tolist()))

    def test_aliased_positional(self):
        df = self.execute('SELECT e.prename FROM employee AS e ORDER BY prename ASC')
        self.assertListEqual(df.prename.tolist(), sorted(self.employees.Prename.tolist()))

    def test_parse_sources(self):
        ids = OdhQLInterpreter.parse_sources('SELECT e.prename FROM ODH12 AS e UNION SELECT c.prename FROM ODH88 AS c')
        self.assertDictEqual(ids, {'ODH12': 12, 'ODH88': 88})

    def test_dup_colnames(self):
        df = self.execute('SELECT e.prename, e.prename, e.surname AS prename FROM employee AS e')
        self.assertListEqual(df.columns.tolist(), ['prename', 'prename2', 'prename3'])

    def test_fails(self):
        statements = (
            ('SELECT e.prename FROM employee AS e ORDER BY nonexistent', 'Non-existent ORDER BY field'),
            ('SELECT e.prename FROM employee AS e ORDER BY e.nonexistent', 'Non-existent ORDER BY field'),
            ('SELECT e.prename FROM employee AS e JOIN child AS c ON c.Parent = e.foobar', 'Non-existent JOIN field'),
            ('SELECT e.prename FROM employee AS e ORDER BY 99', 'Invalid ORDER BY position'),
            ('SELECT e.prename FROM employee AS e UNION SELECT c.age FROM child AS c', 'UNION type mismatch')
        )

        for statement, message in statements:
            try:
                self.assertRaises(OdhQLExecutionException, lambda: self.execute(statement))
            except:
                logging.info(traceback.format_exc())
                self.fail(message)


class TestInterpreterPerformance(TestInterpreterBase):
    @classmethod
    def read_data(cls):
        cls.employees = File.from_file(cls.get_test_file_path('perf/employees.csv')).to_df()[0]
        cls.children = File.from_file(cls.get_test_file_path('perf/children.csv')).to_df()[0]
        cls.source_dfs = {
            'employee': cls.employees,
            'child': cls.children
        }

    def assert_time(self, statement, sec):
        df = self.execute(statement)
        if self.time > sec:
            self.fail('Expected max. execution time of {}s.'.format(sec))
        return df

    def test_select(self):
        self.assert_time('SELECT e.prename FROM employee AS e', 2)

    def test_where(self):
        self.assert_time('SELECT e.prename FROM employee AS e WHERE e.prename = \'Julia\'', 2)

    def test_like(self):
        self.assert_time('SELECT e.prename FROM employee AS e WHERE e.prename LIKE \'^E.+a\'', 3)

    def test_join(self):
        self.assert_time('SELECT c.prename, e.prename AS parent FROM child AS c JOIN employee AS e ON c.parent = e.id',
                         5)

    def test_union(self):
        self.assert_time('SELECT e.prename FROM employee AS e UNION SELECT c.prename FROM child AS c', 3)


if __name__ == '__main__':
    import cProfile

    employees = File.from_file(TestBase.get_test_file_path('perf/employees.csv')).to_df()[0]
    children = File.from_file(TestBase.get_test_file_path('perf/children.csv')).to_df()[0]
    i = OdhQLInterpreter({'employee': employees, 'child': children})
    cProfile.run(
        'i.execute("SELECT c.prename, e.prename AS parent FROM child AS c JOIN employee AS e ON c.parent = e.id")')

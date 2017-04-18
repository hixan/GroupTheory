#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import unittest
# add the root directory to sys.path
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parent.parent))

from GroupTools import *
import itertools
import re

class TestStrs(unittest.TestCase):
    
    def setUp(self):
        self.dt1 = DataTable(["AA","BBB"])
        self.dt2 = DataTable(["AA", "BBAA", "CCAC", "CCB"])
        self.m1 = Mappings(['A', 'B'])
        self.m1.createDefinition()
        self.m1.createDefinition()

    def test_strDataTable(self):
        self.assertEqual(str(self.dt1), ' A A | B B B\n1   1 1     1 ')
        self.assertEqual(str(self.dt2), ' A A | B B A A | C C A C | C C B\n'
                            + '1   1 1       1 1       1 1     1 ')

    def test_strMappings(self):
        self.assertEqual(str(self.m1), ' I A B\n 1 2 3\n 2    \n 3    ')

class Test_Mappings(unittest.TestCase):
    
    def setUp(self):
        self.m1 = Mappings(['A'])
        self.m2 = Mappings(['A', 'B'])
        self.m3 = Mappings('ABCD')
    
    def test_define(self):
        self.m1.define(1, 'A', 2)
        self.m1.define(2, 'A', 3)
        self.assertEqual(str(self.m1), ' I A\n 1 2\n 2 3\n 3  ')
        self.m2.define(1, 'A', 3)
        self.m2.define(1, 'B', 2)
        self.assertEqual(str(self.m2), ' I A B\n 1 3 2\n 2    \n 3    ')
        with self.assertRaises(RuntimeError):
            self.m2.define(1, 'A', 2)

    def test_createDefinition(self):
        for _ in range(3):
            self.m1.createDefinition()
        self.assertEqual(str(self.m1), ' I A\n 1 2\n 2 3\n 3 4\n 4  ')
        self.m2.define(1, 'B', 2)
        self.m2.createDefinition()
        self.assertEqual(str(self.m2), ' I A B\n 1 3 2\n 2    \n 3    ')
        self.m2.createDefinition()
        self.m2.createDefinition()
        self.assertEqual(str(self.m2),
            ' I A B\n 1 3 2\n 2 4 5\n 3    \n 4    \n 5    ')
        self.m3.define(2, 'B', 1)
        self.assertEqual(str(self.m3),
            ' I A B C D\n 1        \n 2   1    ')
        for _ in range(6):
            self.m3.createDefinition()
        self.assertEqual(str(self.m3),
            ' I A B C D\n 1 3 4 5 6\n 2 7 1 8  \n 3        \n'
            # empty lines
            + '\n'.join([' {}        '.format(i) for i in range(4, 9)]))

    def setUpLookups(self):
        for _ in range(4):
            self.m1.createDefinition()
            self.m2.createDefinition()
            self.m3.createDefinition()
        self.m2.define(5, 'B', 2)
        self.m3.define(5, 'D', 3)
        # m1:  m2:     m3:
        # I A  I A B   I A B C D
        # 1 2  1 2 3   1 2 3 4 5
        # 2 3  2 4 5   2        
        # 3 4  3       3        
        # 4 5  4       4        
        # 5    5   2   5       3

    def test_fLookup(self):
        self.setUpLookups()
        for i in range(1, 5):
            self.assertEqual(self.m1.fLookup(i, 'A'), i+1)
        self.assertEqual(self.m2.fLookup(1, 'A'), 2)
        self.assertEqual(self.m2.fLookup(1, 'B'), 3)
        self.assertEqual(self.m2.fLookup(2, 'A'), 4)
        self.assertEqual(self.m2.fLookup(2, 'B'), 5)
        self.assertEqual(self.m2.fLookup(5, 'B'), 2)

        self.assertEqual(self.m3.fLookup(1, 'A'), 2)
        self.assertEqual(self.m3.fLookup(1, 'B'), 3)
        self.assertEqual(self.m3.fLookup(1, 'C'), 4)
        self.assertEqual(self.m3.fLookup(1, 'D'), 5)
        self.assertEqual(self.m3.fLookup(5, 'D'), 3)
        with self.assertRaises(KeyError):
            self.m1.fLookup(5, 'A')
        for n, c in [(3, 'A'), (3, 'B'), (4, 'A'), (4, 'B'), (5, 'A')]:
            with self.assertRaises(KeyError):
                self.m2.fLookup(n, c)
        for c in 'ABCD':
            for n in range(2, 6):
                if c != 'D' and n != 5:
                    with self.assertRaises(KeyError):
                        print('{}{}={}, when it should be undefined'.format(
                            n, c, self.m3.fLookup(n, c)))

    def test_bLookup(self):
        self.setUpLookups()
        for i in range(2, 6):
            self.assertEqual(self.m1.bLookup('A', i), i-1)
        self.assertEqual(self.m2.bLookup('A', 2), 1)
        self.assertEqual(self.m2.bLookup('B', 3), 1)
        self.assertEqual(self.m2.bLookup('A', 4), 2)
        self.assertEqual(self.m2.bLookup('B', 5), 2)

        self.assertEqual(self.m3.bLookup('A', 2), 1)
        self.assertEqual(self.m3.bLookup('B', 3), 1)
        self.assertEqual(self.m3.bLookup('C', 4), 1)
        self.assertEqual(self.m3.bLookup('D', 5), 1)

        with self.assertRaises(KeyError):
            self.m1.bLookup('A', 1)
        defined = {'A':[2, 4], 'B':[3, 5, 2]}
        for c in 'AB':
            for n in range(1, 6):
                if not n in defined[c]:
                    with self.assertRaises(KeyError):
                        print('{}{}={}, when it should be undefined'.format(
                            c, n, self.m2.bLookup(c, n)))
        defined = {'A':[2], 'B':[3], 'C':[4], 'D':[5, 3]}
        for c in 'ABCD':
            for n in range(1, 6):
                if not n in defined[c]:
                    with self.assertRaises(KeyError):
                        print('{}{}={}, when it should be undefined'.format(
                            c, n, self.m3.bLookup(c, n)))

if __name__ == '__main__':
    unittest.main()

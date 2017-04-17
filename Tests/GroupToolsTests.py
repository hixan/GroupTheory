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
        self.m = Mappings(['A', 'B'])
                
                

    def test_strDataTable1(self):


if __name__ == '__main__':
    unittest.main()

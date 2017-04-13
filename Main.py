#!/usr/bin/python3
from copy import copy
from pprint import pprint
import GroupTools

inpt = '<A,B,C | AA, BB, CC, BABCAC, BCABAC>'
print('input: {}'.format(inpt))
a = GroupTools.Group(inpt)

a.solve()
print(str(a))

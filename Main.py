#!/usr/bin/python3
from copy import copy
from pprint import pprint
import GroupTools

#inpt = '<C,A,B|AA,BB,CC,BABCAC,BCABAC>'
inpt = '<A, B, C|AAAA,CC,BB, ABCABC, ABAB, ACAC>'
print('input: {}'.format(inpt))
a = GroupTools.Group(inpt)

a.solve()
print(str(a))

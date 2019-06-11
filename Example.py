#!/usr/bin/python3
from copy import copy
from pprint import pprint
import GroupTools

#inpt = '<C,A,B|AA,BB,CC,BABCAC,BCABAC>'
print("starting")
inpt = '<A, B, C|AAAA,CC,BB, ABCABC, ABAB, ACAC>'
inpt = '<A,B|AAABAAABAAABAAAB,AAAA,BB,AABAAB>'
inpt = '<A,B|AB,AAAA,BBBB'
print('input: {}'.format(inpt))
a = GroupTools.Group(inpt)

a.solve()
print(str(a))

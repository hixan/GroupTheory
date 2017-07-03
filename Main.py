#!/usr/bin/python3
from copy import copy
from pprint import pprint
import GroupTools

#inpt = '<C,A,B|AA,BB,CC,BABCAC,BCABAC>'
print("starting")
inpt = '<A, B, C|AAAA,CC,BB, ABCABC, ABAB, ACAC>'
inpt = '<A,B|AAABAAABAAABAAAB,AAAA,BB,AABAAB>'
print('input: {}'.format(inpt))
a = GroupTools.ToddCoxeter(inpt)

a.solve()
print(str(a))
print(a.m.elementLiterals())

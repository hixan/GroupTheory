#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import re

class DataTable:
    '''table that contains the information about the algorithm, easier to keep track of
    elements rather then getting elements of elements of hashmaps.'''
    def __init__(self, headers):
        '''
        headers - all known independant elements
        '''
        self.data = {}
        for header in headers:
            self.data[header] = [[1]+[None]*(len(header)-1)+[1]]
    def __str__(self):
        numberwidth = 3
        formatnum = '{:<'+str(numberwidth)+'}'
        formatstr = '{:<'+str(numberwidth)+'}'
        strings = []
        for header, rows in self.data.items():
            # TODO: fix this display, the headers need to be seperated by more spaces/other characters.
            # adds header seperated by the right number of spaces.
            strings.append([''.join(map(lambda x:formatstr.format(x), header))])
            for row in rows:
                # adds each row to this column, including headers.
                strings[-1].append(''.join(map(lambda x:formatnum.format(x),
                    map(lambda x : str(x) if x is not None else ' ', row))))
        return '\n'.join(list(map(lambda x : ''.join(x), zip(*strings))))

class Group:
    def __init__(self, string):
        # string like '<A,B,C|AA,BB,CC,BABCAC,BCABAC>'
        string = re.subn(r'[<> ]', '', string)[0]
        splitvals = list(map(lambda x : x.split(','), string.split('|')))
        assert len(splitvals) == 2 # TODO

        self.dt = DataTable(splitvals[1])
        print(str(self.dt))

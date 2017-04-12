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
            self.data[header] = []
        self.addRow()

    def addRow(self):
        for header, rows in self.data.items():
            rows.append([len(rows)+1]+[None]*(len(header)-1)+[len(rows)+1])

    def __str__(self):
        # the length of the longest string that will need to be stored.
        numberwidth = len(str(max(map(len, self.data.values()))))+1
        formatnum = '{:<'+str(numberwidth)+'}'
        formatstr = '{:>'+str(numberwidth)+'}'
        strings = [] # will hold every column as a list, then gets flipped to hold every row as a list
        for header, rows in self.data.items():
            # adds header seperated by the right number of spaces.
            strings.append([''.join(map(lambda x:formatstr.format(x), header))])
            for row in rows:
                # adds each row to this column
                strings[-1].append(''.join(
                    map(lambda x:formatnum.format(x),
                        map(lambda x : str(x) if x is not None else '', row)
                        )
                    ))
        strings = list(zip(*strings)) # transpose of the strings 'matrix' to make concatenation easier
        # headers are offset, then joined with gaps (and pipes to display the gaps) 
        # rows are just concatenated with the addition of a newline between each row.
        return formatstr.format('|').join(strings[0]) + '\n' + \
                '\n'.join(map(lambda x : ''.join(x), strings[1:]))

    def findDefined(self):
        # will find any previously not recorded but mathematically defined elements in the group.
        pass
    
    def putDefined(self, number, letter):
        # eg 1B = 3 will replace None with 3 in all places that it is applicable
        # TODO: handle the case where these are swapped.
        # TODO: this function
        pass


class Mappings:
    def __init__(self, chars):
        self.table = {}
        for char in chars:
            self.table[char] = {}

    def fLookup(self, num, char):
        try:
            return self.table[char][num]
        except KeyError:
            raise KeyError("fLookup: {}{} is not yet defined.".format(num, char))

    def bLookup(self, char, num):
        for key, item in self.table[char]:
            if num == item:
                return key
        raise KeyError("bLookup: {}{} is not yet defined.".format(char, num))
    
    def define(self, num1, char, num2):
        try:
            assert self.table[char][num1] == num2 # make sure that this is not overwriting a previous definition
        except KeyError:
            self.table[char][num1] = num2

    def __str__(self):
        strings = []
        for char, mapping in self.table.values():
            strings.append([char])
        return 'TODO: complete this' # TODO: compelte this.
        


class Group:

    def __init__(self, string):
        # string like '<A,B,C|AA,BB,CC,BABCAC,BCABAC>'
        string = re.subn(r'[<> ]', '', string)[0]
        splitvals = list(map(lambda x : x.split(','), string.split('|')))
        assert len(splitvals) == 2 # TODO proper argument validation
        self.dt = DataTable(splitvals[1])
        self.m = Mappings(splitvals[0])
    
    def __str__(self):
        return str(self.dt) + '\n' + str(self.m)

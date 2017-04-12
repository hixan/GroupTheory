#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import re

class DataTable:
    '''table that contains the information about the algorithm, easier to
    keep track of elements rather then getting elements of elements of
    hashmaps.'''

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
        strings = []
        # will hold every column as a list, then gets flipped to hold every
        # row as a list
        for header, rows in self.data.items():
            # adds header seperated by the right number of spaces.
            strings.append(
                [''.join(map(lambda x:formatstr.format(x), header))])
            for row in rows:
                # adds each row to this column
                strings[-1].append(''.join(map(
                    lambda x:formatnum.format(x),
                    map(lambda x : str(x) if x is not None else '',
                        row))))
        strings = list(zip(*strings))
        # transpose of the strings 'matrix' to make concatenation easier
        # headers are offset, then joined with gaps (and pipes to display
        # the gaps) rows are just concatenated with the addition of a
        # newline between each row.
        return (formatstr.format('|').join(strings[0]) + '\n' + 
                '\n'.join(map(lambda x : ''.join(x), strings[1:])))

    def addDefined(self, mapping):
        # puts all non-previously defined items into the mapping object,
        # and checks integrity of the datastructure.
        for header, rows in self.data.items():
            for row in rows:
                if not None in row:
                    for i in range(len(row)-1):
                        mapping.define(row[i], header[i], row[i+1])
    
    def putDefined(self, mappings):
        def fillRow(row, mappings, header):
            try:
                i = row.index(None)
            except ValueError:
                return
            finally:
                try:
                    row[i] = mappings.fLookup(row[i-1], header[i-1])
                except KeyError:
                    return # stop calculating if value still undefined.
                finally:
                    if None in row:
                        fillRow(row, mappings, header) # keep filling
                    else:
                        self.addDefined(mappings)
                        # the row has been filled, so either:
                        # -a new mapping has been discovered or:
                        # -the closed row is already defined, and can be
                        #   checked for integrity
        for header, rows in self.data.items():
            for row in rows:
                fillRow(row, mappings, header)


class Mappings:
    def __init__(self, chars):
        self.table = {}
        for char in chars:
            self.table[char] = {}
        self.maxDef = 1 # last current elements index.

    def fLookup(self, num, char):
        '''if defined, finds the number that is the result of multiplying
        element number num with element char in that order.

        if not found throws KeyError.'''
        try:
            return self.table[char][num]
        except KeyError:
            raise KeyError("fLookup: {}{} is not yet defined.".format(num,
            char))

    def createDefinition(self, charnum=None):
        '''creates a new definition. throws a ValueError if charnum is
        previously defined or charnum is not of size 2'''
        if charnum is None:
            # assign charnum to the lowest number (first) and earliest char
            # (second) 
            for i in range(1, self.maxDef+1):
                if charnum is not None:
                    break
                for c in self.table.keys():
                    try:
                        self.table[c][i]
                    except KeyError:
                        charnum = (c, i)
                        break
        else:
            if len(charnum) != 2:
                raise ValueError(
                'the length of charnum={} should be 2'.format(str(charnum)))
        self.maxDef += 1
        self.table[charnum[0]][charnum[1]] = self.maxDef


    def bLookup(self, char, num):
        '''looks up the number n1 that satisfies the equation:
        n1 * char = num.'''
        for key, item in self.table[char]:
            if num == item:
                return key
        raise KeyError("bLookup: {}{} is not yet defined.".format(char,
            num))
    
    def define(self, num1, char, num2):
        '''defines new definition in the mapping,
        and makes sure its the same as another if it already exists.'''
        try:
            assert self.table[char][num1] == num2
            # make sure that this is not overwriting a previous definition
        except KeyError:
            self.table[char][num1] = num2

    def __str__(self):
        maxnum = self.maxDef
        formatstr = '{:<'+str(len(str(maxnum))+1)+'}'
        formatnum = '{:>'+str(len(str(maxnum))+1)+'}'
        strings = []
        strings.append(list(self.table.keys()))
        strings[0].insert(0, 'I')
        for i in range(1, maxnum+1):
            strings.append([i])
            for char in strings[0][1:]:
                try:
                    strings[-1].append(self.table[char][i])
                except KeyError:
                    strings[-1].append(None)
        rval = ''.join(map(lambda x:formatstr.format(' '+x), strings[0]))
        rval += '\n'+'\n'.join(map(lambda row :''.join(map(
            lambda x:formatnum.format(str(x) if x is not None else ' '),
            row)), strings[1:]))
        return rval
        


class Group:

    def __init__(self, string):
        """string should be a generator of the form
        <A, B[,*x]|AAA,BB,AAB[,*y]> where x are characters that represent
        linearly independant elements of the group, and y are all strings
        made up of the characters before, and equal the index element"""
        # string like '<A,B,C|AA,BB,CC,BABCAC,BCABAC>'
        string = re.subn(r'[<> ]', '', string)[0]
        splitvals = list(map(lambda x : x.split(','), string.split('|')))
        assert len(splitvals) == 2 # TODO proper argument validation
        self.dt = DataTable(splitvals[1])
        self.m = Mappings(splitvals[0])

    def solve(self):
        pass
    
    def __str__(self):
        return str(self.dt) + '\n' + str(self.m)

#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import traceback
import sys
import re
def debug(func):
    def newFunc(*args, **kwargs):
        print('{m}(\n{a}\n{k}):'.format(
            m=func.__name__, a='\n'.join(map(str, args)),
            k=kwargs if len(kwargs)>0 else ''))
        rval = func(*args, **kwargs)
        print('    {}'.format(rval))
        return rval
    return newFunc


class DataTable:
    '''table that contains the information about the algorithm, easier to
    keep track of elements rather then getting elements of elements of
    hashmaps.
    '''

    def __init__(self, headers):
        '''
        headers - all known independant elements
        '''
        self.data = {}
        for header in headers:
            self.data[header] = []
        self.addRow()

    def _incomplete(self):
        ''':return: True if table is complete (there are no holes)'''
        for rows in self.data.values():
            for row in rows:
                if None in row:
                    return True
        return False

    def addRow(self):
        '''adds new row to data table'''
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
        for header, rows in sorted(self.data.items(), key=lambda x:x[0]):
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
        ''':param mapping: mapping object containing the mappings for this
        DataTable.
        puts all non-previously defined items into the mapping object, and
        checks integrity of the datastructure.'''
        changed = False
        for header, rows in self.data.items():
            for row in rows:
                if not None in row:
                    for i in range(len(row)-1):
                        try:
                            mapping.define(row[i], header[i], row[i+1])
                        except RuntimeError:
                            prevDef = mapping.fLookup(row[i], header[i])
                            if row[i+1] < prevDef:
                                self.replaceWith(prevDef, row[i+1])
                                mapping.overwriteDefine(row[i], header[i],
                                                        row[i+1])
                            else:
                                prevDef = mapping.bLookup(header[i],
                                                            row[i+1])
                                if row[i] < prevDef:
                                    self.replaceWith(prevDef, row[i])
                                    mapping.overwriteDefine(row[i],
                                                    header[i], row[i+1])
                        changed = True
        return changed

    def replaceWith(self, toReplace, newNumber):
        print('replacing all occurances of {} with {}.'.format(toReplace,
                                                                newNumber))
        for rows in self.data.values():
            for row in rows:
                for i in range(len(row)):
                    if row[i] == toReplace:
                        row[i] = newNumber
    
    def putDefined(self, mappings):
        def forfr(row, header, start=0, end=None): # foreward fill row
            if start == end:
                return False
            if end is None:
                end = len(header) - 1
            if row[start] is None:
                return # this return value should never be used
            if row[start+1] is not None:
                # keep going until undefined
                return forfr(row, header, start+1, end)
            try:
                row[start+1] = mappings.fLookup(row[start], header[start])
            except KeyError:
                return False
            finally:
                # keep filling, but return true regardless.
                forfr(row, header, start+1, end)
                return True # this function has changed the row

        def bacfr(row, header, start=0, end=None):
            if start == end:
                return False
            if end is None:
                end = len(header) - 1
            if row[end+1] is None:
                return #this return value should never be used
            if row[end] is not None:
                # keep going until undefined
                return bacfr(row, header, start, end-1)
            try:
                row[end] = mappings.bLookup(header[end], row[end+1])
            except KeyError:
                return False
            finally:
                # keep filling while we can
                bacfr(row, header, start, end-1)
                return True # function has changed row
        
        def fillall():
            # returns true if filling all has changed any values
            changed = False
            for header, rows in self.data.items():
                for row in rows:
                    count = row.count(None)
                    forfr(row, header)
                    bacfr(row, header)
                    if count != row.count(None):
                        changed = True
            return changed

        while fillall(): # while fillall changes self.data
            self.addDefined(mappings) # add all new definitions
        

class Mappings:
    def __init__(self, chars):
        self.table = {}
        for char in chars:
            self.table[char] = {}
        self.maxDef = 1 # last current elements index.

    def overwriteDefine(self, num1, char, num2):
        if self.table[char][num1] != num2:
            self.table[char][num1] = num2
        else:
            raise RuntimeError(
            'trying to redefine definition that is not defined yet\n{}{}{}'
            .format(num1, char, num2))

    def fLookup(self, num, char):
        '''if defined, finds the number that is the result of multiplying
        element number num with element char in that order.

        if not found throws KeyError.'''
        try:
            return self.table[char][num]
        except KeyError:
            raise KeyError('fLookup: {}{} is not yet defined.'.format(num,
            char))

    def elements(self):
        '''iterates through each element, and yields its mappings for each
        independant element'''
        for i in range(1, self.maxDef+1):
            yval = {}
            for key, items in self.table.items():
                yval[key] = items[i]
            yield i, yval

    def createDefinition(self):
        '''creates a new definition at the earliest position available.'''
        # assign charnum to the lowest number (first) and earliest char
        # (second) 
        charnum = None
        for i in range(1, self.maxDef+1):
            if charnum is not None:
                break
            for c in sorted(self.table.keys()):
                try:
                    self.table[c][i] # check this entry is  defined
                except KeyError:
                    charnum = c, i # if not, this is the new definition
                    break
        if charnum is None: # table is full
            return False
        self.define(charnum[1], charnum[0], self.maxDef+1)

    def bLookup(self, char, num):
        '''looks up the number n1 that satisfies the equation:
        n1 * char = num.'''
        for key, item in self.table[char].items():
            if num == item:
                return key
        raise KeyError('bLookup: {}{} is not yet defined.'.format(char,
            num))

    def define(self, num1, char, num2):
        '''defines new definition in the mapping,
        and makes sure its the same as another if it already exists.'''
        #self.table[char] # assure this char exists in the table
        try:
            if self.table[char][num1] != num2:
                raise RuntimeError('{}{} = {} not {}'.format(
                    num1, char, self.table[char][num1], num2))
            # make sure that this is not overwriting a previous definition
        except KeyError:
            print('Defining:', num1, char, num2)
            self.table[char][num1] = num2
            if num2 > self.maxDef:
                self.maxDef = num2
            elif num1 > self.maxDef:
                self.maxDef = num1

    def __str__(self):
        maxnum = self.maxDef
        formatstr = '{:<'+str(len(str(maxnum))+1)+'}'
        formatnum = '{:>'+str(len(str(maxnum))+1)+'}'
        strings = []
        strings.append(list(sorted(self.table.keys())))
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


class ElementFinder:
    
    def __init__(self, m:Mappings):
        self.m = m
        self.table = {}
    
    class E:
        def __init__(self, code:int, *values:str):
            self.code = code
            self.values = values
            for v in values:
                assert type(v) is str
            self.equalities = []
            self.order = None
        def _isMult(self, other1, other2):
            '''other1*other2 = self, so how can self be simplified/
            replesented?'''
            assert type(other1) is E
            assert type(other2) is E
            
            for e1 in other1.equalities:
                for e2 in other2.equalities:
                    self.equalities.append(e1+e2)
            # TODO: simplification and order calculation

        def __eq__(self, other):
            return self.code == other.code
        def __ne__(self, other):
            return not self.__eq__(other)
        def __hash__(self):
            return self.code.__hash__() # TODO: better hashing function
            # although self.values can change, it is only telling us more
            # about the element, and its actual behaviour and properties
            # do not change.


class Group:

    def __init__(self, string):
        """string should be a generator of the form
        <A, B[,*x]|AAA,BB,AAB[,*y]> where x are characters that represent
        linearly independant elements of the group, and y are all strings
        made up of the characters before, and equal the index element"""
        if string is None:
            return
        # string like '<A,B,C|AA,BB,CC,BABCAC,BCABAC>'
        string = re.subn(r'[<> ]', '', string)[0]
        splitvals = list(map(lambda x : x.split(','), string.split('|')))
        assert len(splitvals) == 2 # TODO proper argument validation
        self.dt = DataTable(splitvals[1])
        self.m = Mappings(splitvals[0])

    def addNumber(self):
        '''adds a new entry to this groups datatable and mappings table'''
        if self.m.createDefinition() is False:
            return
        self.dt.addRow()

    def solve(self):
        '''finds all the elements!'''
        while self.dt._incomplete():
            self.addNumber()
            self.dt.putDefined(self.m)
        self.elements = []

    def __str__(self):
        toddc = str(self.dt).split('\n')
        defn = str(self.m).split('\n')
        rval = ('Todd Coxter:' + ' '*(len(toddc[0])-12) + 'Definitions:\n' +
            toddc[0] + '  ' * len(str(self.m.maxDef)) + defn[0])
        for t, d in zip(toddc[1:], defn[1:]):
            rval += '\n' + t + d
        return rval
        #return ('Todd-Coxter algorithm:\n{}\n\nBasic element table: \n{}\n'
            #.format(str(self.dt),str(self.m)))

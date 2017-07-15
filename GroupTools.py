#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
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

    def definitions(self):
        '''generator that returns all elements'''
        for char, mappings in self.table.items():
            for num1, num2 in mappings.items():
                yield num1, char, num2

    def createDefinition(self, dataTable=None):
        '''creates a new definition at the earliest position available.'''
        # assign charnum to the lowest number (first) and earliest char
        # (second) 
        charnum = None
        if dataTable is None:
            for i in range(1, self.maxDef+1):
                if charnum is not None:
                    break
                for c in sorted(self.table.keys()):
                    try:
                        self.table[c][i] # check this entry is  defined
                    except KeyError:
                        charnum = c, i # if not, this is the new definition
                        break
        else:
            def iter(datatable): # TODO implement in DataTable class instead
                for header, rows in datatable.data.items():
                    for row in rows:
                        yield header, row
            # add a definition needed for the row with the smallest number
            # of Nones in it.
            b = False
            for nl in range(1, max(map(len, dataTable.data.keys()))-2):
                # nl = none length
                if b:
                    break
                for header, row in iter(dataTable):
                    if row.count(None) == nl:
                        i = row.index(None)
                        charnum = header[i-1], row[i-1]
                        b = True
                        print('charnum defining', charnum, header, row)
                    if b:
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

    def _allElementLiterals(self):
        rval = {}
        for i in range(self.maxDef):
            rval[i+1] = set()
        rval[1].add('')
        for generator in self.table.keys():
            rval[self.fLookup(1, generator)].add(generator)
        def defined():
            v = set()
            for number, value in rval.items():
                if len(value)>0:
                    v.add(number)
            return v
        while len(defined()) != self.maxDef-1:
            for i in defined():
                for generator in self.table.keys():
                    for equivalent in rval[i]:
                        rval[self.fLookup(i, generator)].add(equivalent+generator)
        return rval

    def elementLiterals(self):
        def order(string):
            rval = len(string)
            for c in string:
                rval *=1000
                rval += ord(c)
            return rval
        rval = {}
        for key, value in self._allElementLiterals().items():
            if len(value)==0:
                continue
            rval[key] = min(value, key=order)
        return rval

    def numberOf(self, element):
        rval = 1
        e = element
        while len(e)>0:
            rval = self.fLookup(rval, element[0])
            e = e[1:]
        return rval

    def operator(self, e1, e2):
        literals = self.elementLiterals()
        rval = literals[self.numberOf(e1+e2)]
        if rval=='':
            return 'I'
        return rval

    '''
    def simplify(self):
        # removes larger numbers of duplicates.
        equiv = []
        for num1, char, num2 in self.definitions():
            for _num1, _char, _num2 in self.definitions():
                if _char == char and _num2 == num2 and num1 != _num1:
                    print(num1, char, num2, _num1, _char, _num2)
                    added = False
                    for elementlist in equiv:
                        if num1 in elementlist:
                            elementlist.append(_num1)
                            added = True
                        elif _num1 in elementlist:
                            elementlist.append(num1)
                            added = True
                    if not added:
                        equiv.append([num1, ])
                        '''

class ToddCoxeter:
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
        if self.m.createDefinition(self.dt) is False:
            return
        self.dt.addRow()

    def solve(self):
        '''finds all the elements!'''
        while self.dt._incomplete():
            self.addNumber()
            self.dt.putDefined(self.m)
            print(self)

    def __str__(self):
        toddc = str(self.dt).split('\n')
        defn = str(self.m).split('\n')
        rval = ('Todd Coxter:' + ' '*(len(toddc[0])-12) + 'Definitions:\n' +
            toddc[0] + '  ' * len(str(self.m.maxDef)) + defn[0])
        for t, d in zip(toddc[1:], defn[1:]):
            rval += '\n' + t + d
        return rval

class Group:
    def __init__(self, elementSet, operation):
        self._operation = operation
        self._elementSet = set()
        self._identity = None
        for element in elementSet:
            self._elementSet.add(Element(self, element))
    def operation(self, element1, element2):
        assert type(element1) == Element and type(element2) == Element
        return self._operation(element1.value, element2.value)

    @property
    def identity(self):
        if identity is None:
            self._findIdentity()
        return self._identity

    def _findIdentity(self):
        ''' finds the identity element in elementSet and sets self._identity. '''
        for element in self._elementSet:
            isIdentity = True
            for e2 in self._elementSet:
                if element * e2 != e2:
                    isIdentity = False
                    break
            if isIdentity:
                self._identity = element
                return

    def centralizer(self, element):
        for element in 

    class Element:
        def __init__(self, group, value):
            self._group = group
            self._value = value
        def __mul__(self, other):
            return self._group.operation(self, other)
        def __eq__(self, other):
            return self.value == other.value and type(self) == type(other)
        def __neq__(self, other):
            return !self.__eq__(other)

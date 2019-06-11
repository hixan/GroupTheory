# Group Theory
This is a module (and example on how to use) about group thoery, and group generators that i wrote to make my math homework easier.

### What can it do?
Currently, it can produce (using the famous [Todd-Coxeter Algorithm](https://en.wikipedia.org/wiki/Todd%E2%80%93Coxeter_algorithm)) all possible elements of a group given its generators. It currently only supports non-inverse elements (so
using standard notation, only capital lettered independant elements; [Helpful Information](http://sporadic.stanford.edu/bump/group/gr1_1.html)) so identity combinations must be converted using the elements order. For Example if inverse(B) == A, AB is equal to the Identity element and so `AB` is added as a representation of the identity element.

### Use
define groups as strings:
```
'<{comma seperated identity elements}|{comma seperated representations of the identity element}>'
```
and pass to the Group object:
```
from FroupTools import Group
inpt = '<A,B|AAAA,AB,BBBB>'
mygroup = Group(inpt)
mygroup.solve()
print(str(mygroup))
```

### Wanted Features
- element multiplication table
- support for inverse elements
- element equivalence calculation
### Changelog
1.0:
  - first working prototype

# Group Theory
This is a module (and example on how to use) about group thoery, and group generators.

### What can it do?
Currently, it can produce (using the famous (Todd-Coxeter Algorithm)[https://en.wikipedia.org/wiki/Todd%E2%80%93Coxeter_algorithm]) all possible elements of a group given its generators. It currently only supports non-inverse elements (so
using standard notation, only capital lettered independant elements; (Helpful Information)[http://sporadic.stanford.edu/bump/group/gr1_1.html]) so identity combinations must be converted using the elements order.

### Use
define groups as strings:
```
'<{comma seperated identity elements}|{comma seperated representations of the identity element}>'
```
and pass to the Group object:
```
from FroupTools import Group
inpt = '<A|AAA>'
mygroup = Group(inpt)
mygroup.solve()
print(str(mygroup))
```

### Wanted Features
	- element multiplication table
	- element equivalence calculation
### Changelog
	1.0:
		first working prototype

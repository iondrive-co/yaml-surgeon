# Yaml Surgeon

## Overview

Precise editing of yaml documents in python or from the command line, where precise means preserving flow style and 
making no unnecessary changes to the remainder of the steam. For example:
```
yaml = """
    - spam:
        - egg: true
        - ham:
            # Lovely
            - spam
        - bacon: [egg, spam]
    - sausage:
        - bacon: [egg, spam]
        - beans: {spam: spam}"""
```
could be edited as follows:
```
output = YamlOperation(yaml).named('bacon').with_parent('spam').duplicate_as('can').then()\
                            .named('egg').with_parent('can').duplicate_as('spam').execute()
```
This inserts a new line `- can: [egg, spam, spam]`, which you can see when you display the final output with 
`print("\n".join(output))`:
```
    - spam:
        - egg: true
        - ham:
            # Lovely 
            - spam
        - bacon: [egg, spam]
        - can: [egg, spam, spam]
    - sausage:
        - bacon: [egg, spam]
        - beans: {spam: spam}
```
To break that down a bit more, the first operation above inserted a `- can: [egg, spam]` line under `- bacon: [egg, spam]`, 
which is the line selected with `.named('bacon').with_parent('spam')` (the `duplicate_as` parameter of `can` was used 
to name the duplicated key). The second operation then inserted a new list entry called `spam` after `egg`, which was 
the list entry selected with `.named('egg').with_parent('can')`. Note the second operation is selecting on the yaml 
document modified by the first operation (the `then` function begins a new operation).

In that example each of the selections was chosen to match exactly one entry, but you can apply operations to multiple
elements, for example you could then do `YamlOperation(output).named('egg').delete().execute()` which would result in:
```
    - spam:
        - ham:
            # Lovely 
            - spam
        - bacon: [spam]
        - can: [spam, spam]
    - sausage:
        - bacon: [spam]
        - beans: {spam: spam}
```
For more details of all of these and other options, please refer to the Guide section below.

## Usage

You can use Yaml Surgeon to edit yaml files by passing in arguments to the main method (see the included PyCharm 
[launcher](./.idea/runConfigurations/yaml_surgeon.xml)), or by importing 
`from yaml_surgeon.yaml_operation import YamlOperation` and building your operation as in the example above. 

This is a quick and dirty implementation which has only been tested with a few simple yaml documents, and it does not 
support many of the more complex yaml features such as multiple parents. Other than that, please use Github issues to 
report any.

Yaml Surgeon is licensed under the License.txt file in the root directory of its source tree.

## Guide to YamlOperation

### Selections

- Selections are used to find parts of a yaml document to apply operations to.
- When a selection matches a mapping key, all elements of the associated mapping value are selected as well.
- Multiple selections are cumulative, meaning each selection acts like an AND in refining the existing selection. 
- Multiple selection operations are commutative, meaning the order you define them does not matter. 
- Multiple selections are allowed to overlap.
- Some selections such as `named` allow more than one parameter in order to perform additive (OR) selections.

#### named() 

Selects all scalars and mappings which exactly match the specified string. For example `.named('egg')` applied to:
```
    - spam:
        - egg:
            - spam
        - ham: [egg]
```
selects both the egg key and associated spam mapping, as well as the egg scalar which is a child of the ham mapping.
It is also possible to select multiple names, for example `.named('egg', 'ham')`

#### name_contains()

Selects all scalars and mappings which contains the specified substring. For example `.name_contains('am')` applied to:
```
    - spam:
        - egg:
            - spam
        - ham: [egg]
```
Selects the top spam mapping, the spam scalar value of the egg mapping, and the ham mapping. It is also possible to 
select multiple substrings, for example `.name_contains('am', 'gg')`

#### named_at_level()

Selects all scalars matching the specified name at the specified level. A level is the number of items deep (starting 
from 0) to look for elements matching the name, with only matching elements on that level being returned. For example 
`.named_at_level('egg', 1)` applied to:
```
    - spam:
        - egg:
            - spam
        - ham: [egg]
```
Selects egg from the egg to spam mapping, but not the egg scalar on the last line.

#### with_parents()

Selects all scalars and mappings whose parent names exactly match the specified string. A parent is a mapping at an 
earlier level that encompasses the element being selected, and we only allow for a single parent (even though yaml 
supports multiple). For example `.with_parent('ham')` applied to:
```
    - spam:
        - bacon:
            - spam:
                - ham
        - ham: [egg]
```
Selects both the ham and egg scalars. It is also possible to select multiple parents, for example `.named('spam', 'egg')`

#### with_parent_at_level()

Selects all scalars and mappings whose parent names exactly match the specified string and which are located at the 
specified level. For example `.with_parent('spam', 1)` applied to:
```
    - spam:
        - bacon:
            - spam:
                - ham
        - spam: [egg]
```
selects only the egg scalar.

### Operations

An operation modifies the yaml document based on the selected text.

#### delete()

Removes the selection from the output. If the selection is a mapping key, then the entire mapping is removed. If the 
selection is a mapping value, then only the value is removed (this is valid yaml). This action may also remove the 
subsequent comma and space (if the selection is in a flow style sequence with elements after it), or the entirety of the 
line (for example if the selection is a sequence element on its own line), or multiple lines (if the selection is a 
mapping key with value covering multiple lines).

For example `.named('egg').delete()` applied to:
```
    - spam:
        - egg:
            - spam
        - ham: [egg]
```
results in
```
    - spam:
        - ham: []
```

#### duplicate_as()

Copies the selection, changes the name of the selection key, and inserts the new selection after the existing one.
For example `.named('ham').duplicate_as('spam')` applied to:
```
    - spam:
        - ham: [egg]
```
results in
```
    - spam:
        - ham: [egg]
        - spam: [egg]
```

#### rename()

Changes the name of the selection key.
For example `.named('ham').rename('spam')` applied to:
```
    - spam:
        - ham: [egg]
```
results in
```
    - spam:
        - spam: [egg]
```
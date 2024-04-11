Surgical editing of yaml documents in python or from the command line, preserving flow style and making no unnecessary 
changes to the remainder of the steam. For example:
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
could be edited with:
```
output = YamlOperation(yaml).named('bacon').with_parent('spam').duplicate_as('can').then()\
                            .named('egg').with_parent('can').duplicate_as('spam').execute()
```
The first operation inserts a `- can: [egg, spam]` line under `- bacon: [egg, spam]`, which is the line selected with 
`.named('bacon').with_parent('spam')` (the `duplicate_as` parameter of `can` was used to name the duplicated key). 
The second operation inserts a new list entry called `spam` after `egg`, which was the list entry selected with 
`.named('egg').with_parent('can')`. Note the second operation is selecting on the yaml document modified by the first 
operation (the `then` function begins a new operation).

Displaying the final output with `print("\n".join(output))` gives:
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
In this example each of the selections was chosen to match exactly one entry, but you can apply operations to multiple
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

You can use yaml surgeon to edit yaml files by passing in arguments to the main method (see the included PyCharm 
[launcher](./.idea/runConfigurations/yaml_surgeon.xml)), or by importing 
`from yaml_surgeon.yaml_operation import YamlOperation` and building your operation as in the example above. 
Please note that this is an early prototype version which has only been tested with a few simple yaml documents, and it 
does not support many of the more complex yaml features such as anchors.

## YamlOperation Selections

- Selections are used to find parts of a yaml document to apply operations to.
- When a selection matches a mapping key, all elements of the associated mapping value are selected as well.
- Multiple selections are cumulative, meaning each selection acts like an AND in refining the existing selection. 
- Multiple selection operations are commutative, meaning the order you define them does not matter. 
- Multiple selections are allowed to overlap.
- Some selections such as `named` allow more than one parameter in order to perform additive (OR) selections. 
- Some selection options take a level, which is the number of items deep (starting from 0) to select elements from 
(i.e. only elements from that level deep in the nesting are examined, not those higher or lower in the yaml structure).

**named()** Selects all scalars and mappings which exactly match the specified string. 
For example `.named('egg')` applied to:
```
    - spam:
        - egg:
            - spam
        - ham: [egg]
```
selects both the egg key and associated spam mapping, as well as the egg scalar which is a child of the ham mapping.
It is also possible to select multiple names, for example `.named('egg', 'ham')`

**name_contains()** Selects all scalars and mappings which contains the specified substring. 
For example `.named('am')` applied to:
```
    - spam:
        - egg:
            - spam
        - ham: [egg]
```
Selects the top spam mapping, the spam scalar value of the egg mapping, and the ham mapping.
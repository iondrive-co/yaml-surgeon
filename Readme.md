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

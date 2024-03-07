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
The first operation chain inserts a `- can: [egg, spam]` line under the line `- bacon: [egg, spam]` (the line was 
duplicated), and the second operation inserts a new list entry called `spam` after egg in the duplicated line (the list
entry was duplicated). Note the second operation is selecting on the yaml document modified by the first operation (the 
`then` function chains the operations). Displaying the final output with `print("\n".join(output))` gives:
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

You can use yaml surgeon to edit yaml files by passing in arguments to the main method (see the included PyCharm 
[launcher](./.idea/runConfigurations/yaml_surgeon.xml)), or by importing 
`from yaml_surgeon.yaml_operation import YamlOperation` and building your operation as in the example above. 
Please note that this is an early prototype version which has only been tested with a few simple yaml documents, and it 
does not support many of the more complex yaml features such as anchors. 

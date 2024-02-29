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
output = YamlOperation(yaml).named('bacon').with_parent('spam').duplicate_as('spam').execute()
print("\n".join(output))
```
which gives
```
    - spam:
        - egg: true
        - ham:
            # Lovely 
            - spam
        - bacon: [egg, spam]
        - spam: [egg, spam]
    - sausage:
        - bacon: [egg, spam]
        - beans: {spam: spam}
```

You can use yaml surgeon to edit yaml files by passing in arguments to the main method (see the included PyCharm 
[launcher](./.idea/runConfigurations/yaml_surgeon.xml)), or by importing 
`from yaml_surgeon.yaml_operation import YamlOperation` and building your operation as in the example above. 
Please note that this is an early prototype version which has only been tested with a few simple yaml documents, and it 
does not support many of the more complex yaml features such as anchors. 

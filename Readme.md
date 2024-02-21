Yaml surgeon is a yaml editor for python. Its raison d'être is to allow "surgical" editing of yaml streams containing
awkward formatting such as mixed flow style structures that other editors would convert to a single style. The design 
philosophy behind this is that we can obtain the information necessary for a large number of useful edit operations via 
a few simple untyped properties rather than imposing a strict type hierarchy.

You can use yaml surgeon to edit yaml files by passing in arguments to the main method (see the included PyCharm 
[launcher](./.idea/runConfigurations/yaml_surgeon.xml)), or by importing 
`from yaml_surgeon.yaml_operation import YamlOperation` and building your operating, for example
`YamlOperation(text_lines).parent('paris').named('server').rename('leader').execute()`

Please note that this is an early prototype version which has only been tested with a few simple yaml documents, and it 
does not support many of the more complex yaml features such as anchors. 

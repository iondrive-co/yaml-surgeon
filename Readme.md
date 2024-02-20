Yaml surgeon is a yaml editor for python. Its raison d'être is to allow editing of
yaml documents that have "awkward" formatting such as mixed flow style structures that
other editors would convert to a single style. The design philosophy that allows this
is to type as little as possible and treat the majority of the elements as strings, this
allows "surgical" modifications to only the desired elements and nothing else. These
modifications can be accessed from either the command line or by importing the module.

This is an early prototype version which has only been tested with a few yaml
documents, and it does not support many of the more complex yaml features such
as anchors yet. It also only supports a few operations, more will be added and
usage documentation added.
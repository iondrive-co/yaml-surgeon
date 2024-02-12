import argparse
from yaml_lexer import scan_text
from yaml_parser import parse_line_tokens


def main():
    parser = argparse.ArgumentParser(description='Process and modify a yaml file')

    parser.add_argument('--filePath', type=str, help='Path to the yaml file')
    parser.add_argument('--name', type=str, help='Name of the node to select')
    parser.add_argument('--childOf', type=str, help='Select only children of a node with this name')
    parser.add_argument('--copy', type=str, help='Name for the copy operation')
    parser.add_argument('--delete', action='store_true', help='Delete the selected nodes')

    args = parser.parse_args()

    with open(args.file_path, 'r') as file:
        text = file.read()
    lexed_lines = scan_text(text)
    parsed_yaml = parse_line_tokens(lexed_lines)

    selector = select(parsed_yaml)

    if args.name:
        selector.name(args.name)
    if args.childOf:
        selector.childOf(args.childOf)
    if args.copy:
        selector.copy(args.copy)
    if args.delete:
        selector.delete()

    result = selector.execute()
    print(result)


class NodeSelector:
    def __init__(self, nodes):
        self.nodes = nodes
        self.selected_nodes = []

    def name(self, name):
        self.selected_nodes = self._recursive_search(self.nodes, name)
        return self

    def _recursive_search(self, nodes, name):
        result = []
        for node in nodes:
            if node.name == name:
                result.append(node)
            result.extend(self._recursive_search(node.children, name))
        return result

    def childOf(self, parent_name):
        self.selected_nodes = find_children_of_node(self.nodes, parent_name)
        return self

    def copy(self, new_name):
        raise NotImplemented

    def delete(self):
        raise NotImplemented

    def execute(self):
        return self.selected_nodes


def select(nodes):
    return NodeSelector(nodes)


def find_children_of_node(nodes, name, level=None):
    result = []

    def search(node, current_level):
        if (level is None or current_level == level) and node.name == name:
            result.extend(node.children)
        elif level is None or current_level < level:
            for child in node.children:
                search(child, current_level + 1)

    for node in nodes:
        search(node, 0)
    return result

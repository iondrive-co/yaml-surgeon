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

    selector = NodeSelector()
    if args.name:
        selector.named(args.name)
    if args.childOf:
        selector.parent(args.childOf)
    if args.copy:
        result = NodeExecutor(selector).copy(args.copy).execute()
    elif args.delete:
        result = NodeExecutor(selector).delete().execute()
    else:
        result = selector.select_on(parsed_yaml)
    print(result)


class NodeSelector:

    def __init__(self):
        self.name = None
        self.parent_name = None

    def named(self, name):
        self.name = name
        return self

    def parent(self, parent_name):
        self.parent_name = parent_name
        return self

    def select_on(self, nodes):
        if self.parent_name is not None:
            selected_nodes = find_children_of_node(nodes, self.parent_name)
        else:
            selected_nodes = nodes
        if self.name is not None:
            selected_nodes = recursive_search(selected_nodes, self.name)
        return selected_nodes


class NodeExecutor:
    def __init__(self, node_selector):
        self.node_selector = node_selector
        self.selected_nodes = []

    def copy(self, new_name):
        raise NotImplemented
        return self

    def delete(self):
        raise NotImplemented
        return self

    def execute(self):
        self.selected_nodes = self.node_selector.select_on()
        return self


def recursive_search(nodes, name):
    result = []
    for node in nodes:
        if node.name == name:
            result.append(node)
        result.extend(recursive_search(node.children, name))
    return result


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

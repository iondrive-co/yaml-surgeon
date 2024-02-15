import argparse
from collections import defaultdict
from yaml_lexer import scan_text
from yaml_parser import parse_line_tokens


class NodeSelector:

    def __init__(self, nodes):
        self.name = None
        self.parent_name = None
        self.nodes = nodes

    def named(self, name):
        self.name = name
        return self

    def parent(self, parent_name):
        self.parent_name = parent_name
        return self

    def select_on(self):
        if self.parent_name is not None:
            selected_nodes = find_children_of_node_called(self.nodes, self.parent_name)
        else:
            selected_nodes = self.nodes
        if self.name is not None:
            selected_nodes = find_nodes_called(selected_nodes, self.name)
        return selected_nodes


class NodeExecutor:
    def __init__(self, node_selector, lexed_lines):
        self.node_selector = node_selector
        self.lexed_lines = lexed_lines
        self.rename_to = None
        self.do_delete = False

    def rename(self, new_name):
        self.rename_to = new_name
        return self

    def delete(self):
        self.do_delete = True
        return self

    def execute(self):
        selected_nodes = self.node_selector.select_on()
        if self.rename_to is not None:
            for node in selected_nodes:
                node.rename(self.rename_to)
        if self.do_delete is True:
            for node in selected_nodes:
                node.rename("")
        return to_lines(selected_nodes, self.lexed_lines)


def find_nodes_called(nodes, name):
    result = []
    for node in nodes:
        if node.name == name:
            result.append(node)
        result.extend(find_nodes_called(node.children, name))
    return result


def find_children_of_node_called(nodes, name, level=None):
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


def create_line_number_map(syntax_nodes):
    line_map = defaultdict(list)

    def add_to_map(node):
        line_map[node.line_number].append(node)
        for child in node.children:
            add_to_map(child)

    for node in syntax_nodes:
        add_to_map(node)

    return dict(sorted(line_map.items()))


def to_lines(nodes, lexed_lines):
    lines = []
    line_node_map = create_line_number_map(nodes)
    for line_number, lexed_line in enumerate(lexed_lines):
        line = ''
        for token in lexed_line.tokens:
            value = token.value
            for node in line_node_map.get(line_number, []):
                # If this value has been modified (we also check for a matching value without the quotes)
                if (node.name == value or node.name.strip('\"') == value) and node.renamed_to is not None:
                    value = node.renamed_to
                    break
            line += value
        lines.append(line)
    return lines


def main():
    parser = argparse.ArgumentParser(description='Process and modify a yaml file')

    parser.add_argument('--filePath', type=str, help='Path to the yaml file')
    parser.add_argument('--name', type=str, help='Name of the node to select')
    parser.add_argument('--childOf', type=str, help='Select only children of a node with this name')
    parser.add_argument('--rename', type=str, help='What to rename the selected to')
    parser.add_argument('--delete', action='store_true', help='Delete the selected nodes')

    args = parser.parse_args()
    print(f"Opening {args.filePath}")
    with open(args.filePath, 'r') as file:
        text = file.read()
    lexed_lines = scan_text(text)
    parsed_yaml = parse_line_tokens(lexed_lines)
    selector = NodeSelector(parsed_yaml)
    if args.name:
        selector.named(args.name)
    if args.childOf:
        selector.parent(args.childOf)
    executor = NodeExecutor(selector, lexed_lines)
    if args.rename:
        executor = executor.rename(args.rename)
    elif args.delete:
        executor = executor.delete()
    lines = executor.execute()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
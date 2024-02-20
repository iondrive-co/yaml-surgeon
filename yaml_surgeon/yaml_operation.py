from collections import defaultdict


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
        if node.name == name or node.name.strip('\"') == name:
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
                if node.name == value and node.renamed_to is not None:
                    value = node.renamed_to
                    break
            line += value
        lines.append(line)
    return lines

from collections import defaultdict


class YamlOperation:

    def __init__(self, nodes, lexed_lines):
        self.nodes = nodes
        self.lexed_lines = lexed_lines
        self.operations = []
        self.selected_nodes = None

    def named(self, name):
        self.operations.append(('named', name))
        return self

    def parent(self, parent_name):
        self.operations.append(('parent', parent_name))
        return self

    def rename(self, new_name):
        self.operations.append(('rename', new_name))
        return self

    def delete(self):
        self.operations.append(('delete',))
        return self

    def get_selected_nodes(self):
        if self.selected_nodes is None:
            self._apply_selections()
        return self.selected_nodes

    def execute(self):
        if self.selected_nodes is None:
            self._apply_selections()

        for op, *args in self.operations:
            if op == 'rename':
                for node in self.selected_nodes:
                    node.rename(args[0])
            elif op == 'delete':
                for node in self.selected_nodes:
                    node.rename("")

        return to_lines(self.selected_nodes, self.lexed_lines)

    def _apply_selections(self):
        self.selected_nodes = self.nodes
        for op, *args in self.operations:
            if op == 'parent':
                self.selected_nodes = find_children_of_node_called(self.selected_nodes, args[0])
        for op, *args in self.operations:
            if op == 'named':
                self.selected_nodes = find_nodes_called(self.selected_nodes, args[0])


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

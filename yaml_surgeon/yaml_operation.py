from collections import defaultdict
from yaml_surgeon.yaml_lexer import scan_text, scan_lines
from yaml_surgeon.yaml_parser import parse_line_tokens


class YamlOperation:

    def __init__(self, nodes_or_yaml, lexed_lines=None):
        if isinstance(nodes_or_yaml, str):
            self.lexed_lines = scan_text(nodes_or_yaml)
            self.nodes = parse_line_tokens(self.lexed_lines)
        else:
            self.nodes = nodes_or_yaml
            self.lexed_lines = lexed_lines
        self.selections = []
        self.operation = None
        self.selected_nodes = None

    def named(self, *names):
        self.selections.append(('named', *names))
        return self

    def name_contains(self, *names):
        self.selections.append(('name_contains', *names))
        return self

    # Note that level starts at 0
    def named_at_level(self, name, level):
        self.selections.append(('named_level', name, level))
        return self

    def with_parents(self, *parent_names):
        self.selections.append(('parent', *parent_names))
        return self

    # Note that level starts at 0
    def with_parent_at_level(self, parent_name, level):
        self.selections.append(('parent_level', parent_name, level))
        return self

    def rename(self, new_name):
        self.operation = ('rename', new_name)
        return self

    def delete(self):
        self.operation = ('delete', None)
        return self

    def duplicate_as(self, name):
        self.operation = ('duplicate', name)
        return self

    def get_selected_nodes(self):
        if self.selected_nodes is None:
            self._apply_selections()
        return self.selected_nodes

    def execute(self):
        self.get_selected_nodes()
        lines_to_delete = []
        flow_entries_to_delete = []
        (op, arg) = self.operation
        if op == 'rename':
            for node in self.selected_nodes:
                node.rename(arg)
        elif op == 'delete':
            for node in self.selected_nodes:
                if node.flow_style:
                    node.rename("")
                    flow_entries_to_delete.append(node.name)
                else:
                    for line_number in range(node.start_line_number, node.end_line_number + 1, 1):
                        lines_to_delete.append(line_number)
        elif op == 'duplicate':
            num_inserted = 0
            for index, node in enumerate(list(self.selected_nodes)):
                if node.flow_style:
                    node.rename(node.name + ", " + arg)
                else:
                    shift_length = node.end_line_number - node.start_line_number + 1
                    # In this case we also duplicate the name so that copy matches on the duplicated line
                    copied_node = node.deep_copy(node.end_line_number + 1).rename(arg)
                    insert_pos = index + 1 + num_inserted
                    self.selected_nodes.insert(insert_pos, copied_node)
                    num_inserted += 1
                    # Move all the other selections down by the shift
                    for i in range(insert_pos + 1, len(self.selected_nodes)):
                        self.selected_nodes[i].shift(shift_length)
                    # Copy everything else about the lines verbatim
                    for i in range(node.start_line_number, node.end_line_number + 1):
                        self.lexed_lines.insert(i + shift_length, self.lexed_lines[i])
        line_node_map = create_line_number_map(self.selected_nodes)
        return to_lines(line_node_map, self.lexed_lines, lines_to_delete, flow_entries_to_delete)

    def then(self):
        # Update the state with the current operations, and reset selectors for another set of operations
        self.lexed_lines = scan_lines(self.execute())
        self.nodes = parse_line_tokens(self.lexed_lines)
        self.selected_nodes = None
        self.selections = []
        self.operation = None
        return self

    def _apply_selections(self):
        self.selected_nodes = self.nodes
        # TODO these are order dependent. Refactor so we can put them in one big loop
        for op, *args in self.selections:
            if op == 'parent':
                self.selected_nodes = find_children_of_node_called(self.selected_nodes, *args, level=None)
        for op, *args in self.selections:
            if op == 'parent_level':
                self.selected_nodes = find_children_of_node_called(self.selected_nodes, args[0], level=args[1])
        for op, *args in self.selections:
            if op == 'named_level':
                level = None if len(args) == 1 else args[1]
                self.selected_nodes = find_nodes_called(self.selected_nodes, args[0], at_level=level)
        for op, *args in self.selections:
            if op == 'named':
                self.selected_nodes = find_nodes_called(self.selected_nodes, *args, at_level=None)
        for op, *args in self.selections:
            if op == 'name_contains':
                self.selected_nodes = find_nodes_containing(self.selected_nodes, *args)


    def _duplicate_node(self, name):
        for i, node in enumerate(self.nodes):
            if node.name == name:
                self.nodes.insert(i + 1, node.deep_copy())
                break


def find_nodes_called(nodes, *names, at_level=None, start_level=0):
    result = []
    for node in nodes:
        if (at_level is None or start_level == at_level) and \
                any(node.name == name or node.name.strip('\"') == name for name in names):
            result.append(node)
        result.extend(find_nodes_called(node.children, *names, at_level=at_level, start_level=start_level + 1))
    return result


def find_nodes_containing(nodes, *names):
    result = []
    for node in nodes:
        if any(name in node.name for name in names):
            result.append(node)
        result.extend(find_nodes_containing(node.children, *names))
    return result


def find_children_of_node_called(nodes, *names, level=None):
    result = []

    def search(node, current_level):
        if (level is None or current_level == level) and any(node.name == name for name in names):
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
        line_map[node.start_line_number].append(node)
        for child in node.children:
            add_to_map(child)

    for node in syntax_nodes:
        add_to_map(node)

    return dict(sorted(line_map.items()))


def to_lines(line_node_map, lexed_lines, lines_to_delete, flow_entries_to_delete):
    lines = []
    for line_number, lexed_line in enumerate(lexed_lines):
        line = ''
        delete_next_connector = False
        delete_next_symbol = False
        for lexed_token in lexed_line.tokens:
            if delete_next_connector and lexed_token.value.strip() == ",":
                lexed_value = ''
                delete_next_connector = False
            elif delete_next_connector and lexed_token.value.strip() == ":":
                lexed_value = ''
                delete_next_symbol = True
            elif delete_next_symbol:
                lexed_value = ''
                delete_next_symbol = False
                delete_next_connector = False
            else:
                delete_next_connector = False
                lexed_value = lexed_token.value
                for node in line_node_map.get(line_number, []):
                    # If this value has been modified
                    if node.name == lexed_value and node.renamed_to is not None:
                        lexed_value = node.renamed_to
                        if node.name in flow_entries_to_delete:
                            delete_next_connector = True
                        break
            line += lexed_value
        if line_number not in lines_to_delete:
            lines.append(line)
    return lines

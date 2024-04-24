

class Token:
    def __init__(self, value, types):
        self.value = value
        # Types can be Comment, Sequence, Mapping, or Scalar
        self.types = types

    def __eq__(self, other):
        if isinstance(other, Token):
            return (self.value == other.value and
                    self.types == other.types)
        return False

    def __repr__(self):
        return f"Token(value='{self.value}', " \
               f"types={self.types})"


class Line:
    def __init__(self, tokens, line_number, level):
        # These are the Tokens from scanning the line
        self.tokens = tokens
        self.line_number = line_number
        self.level = level

    def __eq__(self, other):
        if isinstance(other, Line):
            return (self.tokens == other.tokens and
                    self.line_number == other.line_number and
                    self.level == other.level)
        return False

    def __repr__(self):
        return f"Line(tokens='{self.tokens}', " \
               f"line_number={self.line_number}', " \
               f"level={self.level})"


class SyntaxNode:
    def __init__(self, name, line_number, flow_style=""):
        self.name = name
        self.renamed_to = None
        self.start_line_number = line_number
        self.end_line_number = line_number
        self.children = []
        self.flow_style = flow_style

    def add_child(self, child):
        self.children.append(child)
        self.extend_end(child.end_line_number)

    def extend_end(self, new_end_line_number):
        self.end_line_number = max(self.end_line_number, new_end_line_number)

    def rename(self, renamed_to):
        self.renamed_to = renamed_to
        return self

    def deep_copy(self, insert_at_line):
        # This copies the node to a position immediately under its last child
        copied_node = SyntaxNode(self.name, insert_at_line, self.flow_style)
        copied_node.renamed_to = self.renamed_to
        for child in self.children:
            child_depth = child.start_line_number - self.start_line_number
            copied_child = child.deep_copy(insert_at_line + child_depth)
            copied_node.add_child(copied_child)
        return copied_node

    def shift(self, shift_amount):
        self.start_line_number += shift_amount
        self.end_line_number += shift_amount
        for child in self.children:
            child.shift(shift_amount)

    def __eq__(self, other):
        if isinstance(other, SyntaxNode):
            return (self.name == other.name and
                    self.start_line_number == other.start_line_number and
                    self.end_line_number == other.end_line_number and
                    self.renamed_to == other.renamed_to and
                    self.flow_style == other.flow_style and
                    self.children == other.children)
        return False

    def __repr__(self):
        return f"SyntaxNode(name='{self.name}', " \
               f"start_line_number='{self.start_line_number}', " \
               f"end_line_number='{self.end_line_number}', " \
               f"renamed_to='{self.renamed_to}', " \
               f"flow_style='{self.flow_style}', " \
               f"children={self.children})"

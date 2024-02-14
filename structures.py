

class Token:
    def __init__(self, value, types):
        self.value = value
        # Types can be Comment, List, Dict, or Scalar
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
    def __init__(self, name, line_number):
        self.name = name
        self.line_number = line_number
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __eq__(self, other):
        if isinstance(other, SyntaxNode):
            return (self.name == other.name and
                    self.line_number == other.line_number and
                    self.children == other.children)
        return False

    def __repr__(self):
        return f"SyntaxNode(name='{self.name}', " \
               f"line_number='{self.line_number}', " \
               f"children={self.children})"

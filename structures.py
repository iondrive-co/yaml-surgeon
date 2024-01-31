class Line:
    def __init__(self, text, line_number, level):
        self.text = text
        self.line_number = line_number
        self.level = level
        self.types = []

    def add_type(self, node):
        self.types.append(node)

    def __eq__(self, other):
        if isinstance(other, Line):
            return (self.text == other.text and
                    self.line_number == other.line_number and
                    self.level == other.level and
                    self.types == other.types)
        return False

    def __repr__(self):
        return f"Line(text='{self.text}', " \
               f"line_number={self.line_number}', " \
               f"level={self.level}', " \
               f"types={self.types})"


class Token:
    def __init__(self, type, value, parent):
        self.type = type
        self.value = value
        self.parent = parent

    def __eq__(self, other):
        if isinstance(other, Token):
            return (self.type == other.type and
                    self.value == other.value and
                    self.parent == other.parent)
        return False

    def __repr__(self):
        return f"Token(type='{self.type}', " \
               f"value={self.value}', " \
               f"parent={self.parent})"
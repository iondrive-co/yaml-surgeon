from enum import Enum


class Line:
    def __init__(self, text_elements, line_number, level):
        self.text_elements = text_elements
        self.line_number = line_number
        self.level = level

    def __eq__(self, other):
        if isinstance(other, Line):
            return (self.text_elements == other.text_elements and
                    self.line_number == other.line_number and
                    self.level == other.level)
        return False

    def __repr__(self):
        return f"Line(text_elements='{self.text_elements}', " \
               f"line_number={self.line_number}', " \
               f"level={self.level})"


class Token:
    def __init__(self, value, line_num, element_num):
        self.value = value
        self.line_num = line_num
        self.element_num = element_num

    def __eq__(self, other):
        if isinstance(other, Token):
            return (self.value == other.value and
                    self.line_num == other.line_num and
                    self.element_num == other.element_num)
        return False

    def __repr__(self):
        return f"Token(value='{self.value}', " \
               f"line_num={self.line_num}', " \
               f"element_num={self.element_num})"

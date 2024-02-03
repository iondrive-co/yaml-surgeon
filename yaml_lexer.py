from structures import Line, Token
import re


def scan_text(text):
    """
    Build an ordered list of Line objects from the specified text, including calculating the nesting level
    of each line. We preserve all data including spaces as we don't want to make any unnecessary modifications
    """
    lines = text.splitlines()
    if not lines:
        return []
    yaml_lines = []
    nesting_level = 0
    previous_indent = len(lines[0]) - len(lines[0].lstrip())
    block_indent_amounts = []
    for line_number, line in enumerate(lines):
        current_indent = len(line) - len(line.lstrip())
        if current_indent > previous_indent:
            block_indent_amounts.append(current_indent - previous_indent)
            nesting_level += 1
        elif current_indent < previous_indent:
            # We can unindent by one or more of the stacked block indent amounts
            indent_decrease = previous_indent - current_indent
            while indent_decrease > 0:
                if not block_indent_amounts:
                    raise SyntaxError(f"Indent to the left of the start on line {line_number}: {line}")
                indent_decrease -= block_indent_amounts.pop()
                nesting_level -= 1
        line_elements = split_nested_structures(line)
        yaml_lines.append(Line(line_elements, line_number + 1, nesting_level))
        previous_indent = current_indent
    return yaml_lines


def split_nested_structures(line):
    tokens = []
    buffer = ""
    i = 0
    length = len(line)
    while i < length:
        char = line[i]
        i += 1
        if char == '[':
            buffer += char
            # Include whitespace characters after '[' in the existing buffer
            while i < length and line[i].isspace():
                buffer += line[i]
                i += 1
            # Include quote characters after that in the existing buffer
            if i < length and line[i] in ["'", '"']:
                buffer += line[i]
                i += 1
            # Add what we have to tokens, and start a new buffer
            tokens.append(buffer)
            buffer = ""
        elif char in ["'", '"']:
            tokens.append(buffer)
            buffer = char
        elif char in [']', ','] and not line[i - 2].isspace():
            tokens.append(buffer)
            buffer = char
        elif char.isspace():
            j = i
            # Skip over any more whitespace
            while j < length and line[j].isspace():
                j += 1
            # If the non-whitespace character is a closer, then we don't want the j text and should split now
            if j < length and line[j] in [']', ',']:
                tokens.append(buffer)
                buffer = char
            else:
                buffer += char
        elif char.isalnum and len(buffer) > 0 and buffer[0] == ',':
            tokens.append(buffer)
            buffer = char
        else:
            buffer += char
    tokens.append(buffer)
    return tokens


def parse_line_tokens(lines):
    """
    Takes ordered list of Line objects as obtained from scan_text, and parses their contents
    in order to assign yaml tokens to each line element. Returns the yaml tokens organised into a tree structure
    """
    level_parents = {}
    for line in lines:
        for token in tokens:
            level_parents[line.level] = token
            if line.level - 1 in level_parents and token.type != TokenType.SCALAR:
                token.set_parent(level_parents[line.level - 1])
            line.add_type(token)


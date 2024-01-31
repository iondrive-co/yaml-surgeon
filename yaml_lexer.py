from structures import Line, Token, TokenType


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
        yaml_lines.append(Line(line, line_number + 1, nesting_level))
        previous_indent = current_indent
    return yaml_lines


def parse_line_tokens(lines):
    """
    Takes ordered list of Line objects as obtained from scan_text, and parses their contents
    in order to assign yaml tokens to each line
    """
    for line in lines:
        tokens = []
        # TODO could be multiple per line
        if line.startswith('- '):
            tokens.append(Token(TokenType.LIST, line[2:].strip()))
        elif line.startswith('#'):
            tokens.append(Token(TokenType.METADATA, line[1:].strip()))
        elif line.strip == "..." or not line.strip():
            tokens.append(Token(TokenType.METADATA, line.strip()))
        elif ': ' in line or line.endswith(':'):
            # Splitting for dict key and possible inline values
            key, *inline_values = line.split(':', 1)
            key = key.strip()
            values = [key]
            if inline_values:
                # Process inline values (e.g., [fast, secure])
                inline_values = inline_values[0].strip().strip('[]').split(',')
                values.extend(value.strip() for value in inline_values)
            # TODO only takes one value
            tokens.append(Token(TokenType.DICTIONARY, values))
        else:
            tokens.append(Token(TokenType.SCALAR, line.strip()))
        # TODO add to line, set parent


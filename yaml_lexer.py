from structures import Line


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
    block_indent_amount = 2
    for line_number, line in enumerate(lines):
        current_indent = len(line) - len(line.lstrip())
        if current_indent > previous_indent:
            block_indent_amount = current_indent - previous_indent
            nesting_level += 1
        elif current_indent < previous_indent:
            # We can unindent by one or more multiple of the current block indent amount
            nesting_level -= (previous_indent - current_indent) / block_indent_amount
            if not nesting_level.is_integer():
                raise SyntaxError(f"Indent on line {line_number} is not a multiple of the block indent")
            if nesting_level < 0:
                raise SyntaxError(f"Indent to the left of the start on line {line_number}")
        yaml_lines.append(Line(line, line_number + 1, nesting_level))
        previous_indent = current_indent
    return yaml_lines





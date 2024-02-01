from structures import Line, Token, TokenType
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
        yaml_lines.append(Line(line, line_number + 1, nesting_level))
        previous_indent = current_indent
    return yaml_lines


def parse_line_tokens(lines):
    """
    Takes ordered list of Line objects as obtained from scan_text, and parses their contents
    in order to assign yaml tokens to each line
    """
    level_parents = {}
    for line in lines:
        tokens = []
        if line.text.startswith('- '):
            # Handle list items
            tokens.append(Token(TokenType.LIST, line.text[2:].strip()))
        elif line.text.startswith('#') or line.text.strip() == "..." or not line.text.strip():
            # Handle metadata
            tokens.append(Token(TokenType.METADATA, line.text.strip()))
        elif ': ' in line.text or line.text.endswith(':'):
            # Handle dictionary keys and possible inline values
            key, *inline_values = line.text.split(':', 1)
            key = key.strip()
            key_token = Token(TokenType.DICTIONARY, key)
            tokens.append(key_token)
            if inline_values:
                # Further split inline values if they exist
                inline_values = re.split(r',\s*(?![^[]*\])', inline_values[0].strip())
                for value in inline_values:
                    value = value.strip().strip('[]{}')
                    if value:
                        value_tokens = [Token(TokenType.SCALAR, v.strip()) for v in value.split(',')]
                        for vt in value_tokens:
                            vt.set_parent(key_token)
                        tokens.extend(value_tokens)
        else:
            # Handle scalar values
            tokens.append(Token(TokenType.SCALAR, line.text.strip()))

        for token in tokens:
            level_parents[line.level] = token
            if line.level - 1 in level_parents and token.type != TokenType.SCALAR:
                token.set_parent(level_parents[line.level - 1])
            line.add_type(token)


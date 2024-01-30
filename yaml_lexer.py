from structures import YamlLine


def scan_text(text):
    """
    Build a list of YamlLines from the specified text, calculating the indentation level.
    """
    lines = text.strip().split("\n")
    yaml_lines = []
    previous_indent = 0
    for line_number, line in enumerate(lines):
        current_indent = len(line) - len(line.lstrip())

        if line.strip() == "":
            # Skip empty lines for level calculation
            level = 0
        elif current_indent > previous_indent:
            level = yaml_lines[-1].level + 1 if yaml_lines else 0
        elif current_indent < previous_indent:
            # Find a line with matching or lesser indent to determine level
            level = next((yl.level for yl in reversed(yaml_lines) if len(yl.text) - len(yl.text.lstrip()) <= current_indent), 0)
        else:
            level = yaml_lines[-1].level if yaml_lines else 0

        yaml_lines.append(YamlLine(line, line_number + 1, level))
        previous_indent = current_indent

    return yaml_lines





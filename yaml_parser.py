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
from structures import SyntaxNode


def parse_line_tokens(lines):
    """
    Takes and ordered list of Line objects as obtained from the lexer, and parses their contents to produce an abstract
    syntax represenation of the type and relationships of the yaml elements
    """
    level_parents = {}
    nodes = []
    for line in lines:
        level = line.level
        # Keep track of what we have already seen on this line
        line_has_dict = False
        line_has_comment = False
        line_has_scalar = False
        for token in line.tokens:
            if line_has_comment:
                break
            for token_type in token.types:
                if token_type == 'Comment':
                    # We are done with this line, there is nothing in the remaining tokens we need
                    line_has_comment = True
                    break
                elif token_type == 'Scalar':
                    # If this line already has a scalar and no nested structures, add this one as a child
                    if line_has_scalar and level == line.level:
                        level_parents[level].add_child(SyntaxNode(token.value))
                    else:
                        level_parents[level] = SyntaxNode(token.value)
                        if level == 0:
                            nodes.append(level_parents[level])
                        else:
                            level_parents[level - 1].add_child(level_parents[level])
                    line_has_scalar = True
                elif token_type == 'Dict':
                    if line_has_dict:
                        # Second dict token makes this a flow style nested dictionary
                        level += 1
                    else:
                        line_has_dict = True
                elif token_type == 'List' and line_has_dict:
                    # This is a flow style nested list
                    level += 1
    return nodes

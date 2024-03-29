from yaml_surgeon.structures import SyntaxNode


def parse_line_tokens(lines):
    """
    Takes an ordered list of Line objects as obtained from the lexer, and parses their contents to produce an abstract
    syntax map of line numbers to SyntaxNodes on the line, representing the type and relationships of the yaml elements
    """
    level_parents = {}
    nodes = []
    for line_number, line in enumerate(lines):
        level = line.level
        # Keep track of what we have already seen on this line
        line_has_dict = False
        line_has_comment = False
        line_has_scalar = False
        line_has_flow_style = False
        for token in line.tokens:
            if line_has_comment:
                break
            for token_type in token.types:
                if token_type == 'Comment':
                    # We are done with this line, there is nothing in the remaining tokens we need
                    line_has_comment = True
                    break
                elif token_type == 'Scalar':
                    node = SyntaxNode(token.value, line_number, line_has_flow_style)
                    # If this line already has a scalar and no nested structures, add this one as a child
                    if line_has_scalar and level == line.level:
                        level_parents[level].add_child(node)
                    else:
                        level_parents[level] = node
                        prev_level = level - 1
                        if level == 0 or prev_level not in level_parents:
                            nodes.append(node)
                        else:
                            level_parents[prev_level].add_child(level_parents[level])
                            # Make sure all ancestors have their end line extended to the current line
                            while prev_level in level_parents:
                                level_parents[prev_level].extend_end(level_parents[level].end_line_number)
                                prev_level = prev_level - 1
                    line_has_scalar = True
                elif token_type == 'Dict':
                    if line_has_dict:
                        # Second dict token makes this a flow style nested dictionary
                        line_has_flow_style = True
                        level += 1
                    else:
                        line_has_dict = True
                elif token_type == 'List' and line_has_dict:
                    # This is a flow style nested list
                    line_has_flow_style = True
                    level += 1
    return nodes

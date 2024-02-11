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
        line_has_dict = False
        line_has_comment = False
        for token in line.tokens:
            if line_has_comment:
                break
            for token_type in token.types:
                if token_type == 'Comment':
                    # We are done with this line, there is nothing in the remaining tokens we need
                    line_has_comment = True
                    break
                elif token_type == 'Scalar':
                    level_parents[level] = SyntaxNode(token.value)
                    if level == 0:
                        nodes.append(level_parents[level])
                    else:
                        level_parents[level - 1].add_child(level_parents[level])
                elif token_type == 'Dict':
                    if line_has_dict:
                        # This is a flow style nested dictionary
                        level += 1
                    else:
                        line_has_dict = True
                elif token_type == 'List' and line_has_dict:
                    # This is a flow style nested list
                    level += 1
    return nodes


def find_children_of_node(nodes, name, level=None):
    result = []

    def search(node, current_level):
        if (level is None or current_level == level) and node.name == name:
            result.extend(node.children)
        elif level is None or current_level < level:
            for child in node.children:
                search(child, current_level + 1)

    for node in nodes:
        search(node, 0)
    return result

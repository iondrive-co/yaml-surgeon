import unittest
from yaml_lexer import scan_text
from yaml_parser import parse_line_tokens
from yaml_operation import find_children_of_node, select
from structures import SyntaxNode


class TestFindChildren(unittest.TestCase):

    @staticmethod
    def load_yaml_samples(file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        samples = text.split('[yaml')
        return {f"yaml{i}": sample.split(']', 1)[1].strip() for i, sample in enumerate(samples) if sample.strip()}

    def test_find_children_of_node_valid_list_nested_dict(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml1"]
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        result = find_children_of_node(parsed_yaml, 'settings')
        expected = [SyntaxNode('fast'), SyntaxNode('secure'), SyntaxNode('reliable'), SyntaxNode('scalable')]
        assert_syntax_nodes_equal(expected, result)

        result_level = find_children_of_node(parsed_yaml, 'serverConfig', 0)
        expected = [SyntaxNode('srv-100'), SyntaxNode('srv-200')]
        assert_syntax_nodes_equal(expected, result_level)

    def test_find_children_of_node_valid_list_nested_dict_yaml2(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml2"]
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        result = find_children_of_node(parsed_yaml, 'labels')
        expected = [SyntaxNode('app'), SyntaxNode('steps')]
        assert_syntax_nodes_equal(expected, result)

        result_level = find_children_of_node(parsed_yaml, 'metadata', 0)
        expected = [SyntaxNode('name'), SyntaxNode('labels')]
        assert_syntax_nodes_equal(expected, result_level)

    def test_find_children_of_node_valid_list_nested_dict_yaml3(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml3"]
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        result = find_children_of_node(parsed_yaml, 'metadata')
        expected = [SyntaxNode('build'), SyntaxNode('resources'), SyntaxNode('emptyLabel')]
        assert_syntax_nodes_equal(expected, result)

        result_level = find_children_of_node(parsed_yaml, 'kind', 0)
        expected = [SyntaxNode('Pod')]
        assert_syntax_nodes_equal(expected, result_level)


def assert_syntax_nodes_equal(expected, actual):
    assert len(expected) == len(actual), f"Expected {len(expected)} nodes, found {len(actual)} nodes"
    for exp_node, act_node in zip(expected, actual):
        assert exp_node.name == act_node.name, f"Expected node name '{exp_node.name}', found '{act_node.name}'"


def create_test_tree():
    root = SyntaxNode('root')
    child1 = SyntaxNode('child1')
    child2 = SyntaxNode('child2')
    grandchild1 = SyntaxNode('grandchild1')
    grandchild2 = SyntaxNode('grandchild2')

    root.add_child(child1)
    root.add_child(child2)
    child1.add_child(grandchild1)
    child2.add_child(grandchild2)

    return [root, child1, child2]


class TestNodeSelector(unittest.TestCase):

    def test_node_selector_yaml_1(self):
        yaml_content = """- parent1:
            - srv-100:
                fast: true
        - parent2:
            - srv-100:
                secure: true
        - database:
            - srv-300
        - webApp"""
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)
        selected_nodes = select(parsed_yaml).name('srv-100').execute()
        self.assertEqual(len(selected_nodes), 2)
        self.assertEqual(selected_nodes[0].name, 'srv-100', 'srv-100')

        selected_nodes = select(parsed_yaml).name('srv-100').childOf('parent2').execute()
        self.assertEqual(len(selected_nodes), 1)
        self.assertEqual(selected_nodes[0].name, 'srv-100')
        child_names = [child.name for child in selected_nodes[0].children]
        self.assertIn('secure', child_names)


if __name__ == '__main__':
    unittest.main()

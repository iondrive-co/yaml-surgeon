import unittest
from yaml_surgeon.yaml_lexer import scan_text
from yaml_surgeon.yaml_parser import parse_line_tokens
from yaml_surgeon.yaml_operation import find_children_of_node_called,create_line_number_map
from yaml_surgeon.structures import SyntaxNode


class TestHelpers(unittest.TestCase):

    @staticmethod
    def load_yaml_sample(file_name):
        with open("../../samples/" + file_name, 'r') as file:
            text = file.read()
        return text

    def test_find_children_of_node_valid_sequence_nested_mapping(self):
        yaml_content = self.load_yaml_sample("valid1.yaml")
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        result = find_children_of_node_called(parsed_yaml, 'settings')
        expected = [SyntaxNode('fast', 2), SyntaxNode('secure', 2), SyntaxNode('reliable', 4), SyntaxNode('scalable', 4)]
        assert_syntax_nodes_equal(expected, result)

        result_level = find_children_of_node_called(parsed_yaml, 'serverConfig', 0)
        expected = [SyntaxNode('srv-100', 1), SyntaxNode('srv-200', 3)]
        assert_syntax_nodes_equal(expected, result_level)

    def test_find_children_of_node_valid_sequence_nested_mapping_yaml2(self):
        yaml_content = self.load_yaml_sample("valid2.yaml")
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        result = find_children_of_node_called(parsed_yaml, 'labels')
        expected = [SyntaxNode('app', 5), SyntaxNode('steps', 6)]
        assert_syntax_nodes_equal(expected, result)

        result_level = find_children_of_node_called(parsed_yaml, 'metadata', 0)
        expected = [SyntaxNode('name', 3), SyntaxNode('labels', 4)]
        assert_syntax_nodes_equal(expected, result_level)

    def test_find_children_of_node_valid_sequence_nested_mapping_yaml3(self):
        yaml_content = self.load_yaml_sample("valid3.yaml")
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        result = find_children_of_node_called(parsed_yaml, 'metadata')
        expected = [SyntaxNode('build', 5), SyntaxNode('resources', 6), SyntaxNode('emptyLabel', 8)]
        assert_syntax_nodes_equal(expected, result)

        result_level = find_children_of_node_called(parsed_yaml, 'kind', 0)
        expected = [SyntaxNode('Pod', 2)]
        assert_syntax_nodes_equal(expected, result_level)

    def test_create_line_number_map(self):
        serverConfig = SyntaxNode('serverConfig', '0')
        srv100 = SyntaxNode('srv-100', '1')
        settings100 = SyntaxNode('settings', '2')
        settings100.add_child(SyntaxNode('fast', '2'))
        settings100.add_child(SyntaxNode('secure', '2'))
        srv100.add_child(settings100)

        srv200 = SyntaxNode('srv-200', '3')
        settings200 = SyntaxNode('settings', '4')
        settings200.add_child(SyntaxNode('reliable', '4'))
        settings200.add_child(SyntaxNode('scalable', '4'))
        srv200.add_child(settings200)
        backup_to = SyntaxNode('backup_to', '5')
        backup_to.add_child(SyntaxNode('storageUnit', '5'))
        srv200.add_child(backup_to)

        serverConfig.add_child(srv100)
        serverConfig.add_child(srv200)

        database = SyntaxNode('database', '6')
        srv300 = SyntaxNode('srv-300', '7')
        database.add_child(srv300)

        webApp = SyntaxNode('webApp', '8')

        syntax_nodes = [serverConfig, database, webApp]

        line_map = create_line_number_map(syntax_nodes)

        self.assertIn('0', line_map)
        self.assertIn('1', line_map)
        self.assertIn('2', line_map)
        self.assertIn('3', line_map)
        self.assertIn('4', line_map)
        self.assertIn('5', line_map)
        self.assertIn('6', line_map)
        self.assertIn('7', line_map)
        self.assertIn('8', line_map)

        self.assertEqual(len(line_map['2']), 3, "There should be three nodes on line 2")
        self.assertEqual(len(line_map['4']), 3, "There should be three nodes on line 4")
        self.assertEqual(len(line_map['5']), 2, "There should be two nodes on line 5")


def assert_syntax_nodes_equal(expected, actual):
    assert len(expected) == len(actual), f"Expected {len(expected)} nodes, found {len(actual)} nodes"
    for exp_node, act_node in zip(expected, actual):
        assert exp_node.name == act_node.name, f"Expected node name '{exp_node.name}', found '{act_node.name}'"


if __name__ == '__main__':
    unittest.main()
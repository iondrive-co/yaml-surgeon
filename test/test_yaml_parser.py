import unittest
from yaml_lexer import scan_text
from yaml_parser import parse_line_tokens, find_children_of_node
from structures import SyntaxNode


class TestParseYaml(unittest.TestCase):

    @staticmethod
    def load_yaml_samples(file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        samples = text.split('[yaml')
        return {f"yaml{i}": sample.split(']', 1)[1].strip() for i, sample in enumerate(samples) if sample.strip()}

    def test_parse_valid_list_nested_dict(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml1"]
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        serverConfig = SyntaxNode('serverConfig')
        srv100 = SyntaxNode('srv-100')
        settings100 = SyntaxNode('settings')
        settings100.add_child(SyntaxNode('fast'))
        settings100.add_child(SyntaxNode('secure'))
        srv100.add_child(settings100)

        srv200 = SyntaxNode('srv-200')
        settings200 = SyntaxNode('settings')
        settings200.add_child(SyntaxNode('reliable'))
        settings200.add_child(SyntaxNode('scalable'))
        srv200.add_child(settings200)
        backup_to = SyntaxNode('backup_to')
        srv200.add_child(backup_to)
        backup_to.add_child(SyntaxNode('storageUnit'))

        serverConfig.add_child(srv100)
        serverConfig.add_child(srv200)

        database = SyntaxNode('database')
        srv300 = SyntaxNode('srv-300')
        database.add_child(srv300)

        webApp = SyntaxNode('webApp')

        expected = [serverConfig, database, webApp]
        self.assertEqual(expected, parsed_yaml)

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

    def test_parse_valid_list_nested_dict_yaml2(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml2"]
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        apiVersion = SyntaxNode('apiVersion')
        apiVersion.add_child(SyntaxNode('v1'))
        kind = SyntaxNode('kind')
        kind.add_child(SyntaxNode('Pod'))
        metadata = SyntaxNode('metadata')
        name = SyntaxNode('name')
        name.add_child(SyntaxNode('apache-pod'))
        labels = SyntaxNode('labels')
        app = SyntaxNode('app')
        app.add_child(SyntaxNode('web'))
        steps = SyntaxNode('steps')
        step1 = SyntaxNode('uses')
        step1.add_child(SyntaxNode('actions/checkout@v2'))
        step2 = SyntaxNode('name')
        step2.add_child(SyntaxNode('Set up Python'))
        steps.add_child(step1)
        steps.add_child(step2)
        labels.add_child(app)
        labels.add_child(steps)
        metadata.add_child(name)
        metadata.add_child(labels)

        expected = [apiVersion, kind, metadata]
        self.assertEqual(expected, parsed_yaml)

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

    def test_parse_valid_list_nested_dict_yaml3(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml3"]
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        kind = SyntaxNode('kind')
        kind.add_child(SyntaxNode('Pod'))
        metadata = SyntaxNode('metadata')
        build = SyntaxNode('build')
        build.add_child(SyntaxNode('"2020-01-01"'))
        resources = SyntaxNode('resources')
        emptyLabel = SyntaxNode('emptyLabel')
        metadata.add_child(build)
        metadata.add_child(resources)
        metadata.add_child(emptyLabel)

        expected = [kind, metadata]
        self.assertEqual(expected, parsed_yaml)

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


if __name__ == '__main__':
    unittest.main()

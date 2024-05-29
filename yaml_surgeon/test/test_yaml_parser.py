import unittest
from yaml_surgeon.yaml_lexer import scan_text
from yaml_surgeon.yaml_parser import parse_line_tokens
from yaml_surgeon.structures import SyntaxNode


class TestParseYaml(unittest.TestCase):

    @staticmethod
    def load_yaml_sample(file_name):
        with open("../samples/" + file_name, 'r') as file:
            text = file.read()
        return text

    def test_parse_valid_sequence_nested_mapping(self):
        yaml_content = self.load_yaml_sample("valid1.yaml")
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        server_config = SyntaxNode('serverConfig', 0, is_block_sequence=True)
        srv100 = SyntaxNode('srv-100', 1, is_block_sequence=True)
        settings100 = SyntaxNode('settings', 2)
        settings100.add_child(SyntaxNode('fast', 2, flow_style="Sequence"))
        settings100.add_child(SyntaxNode('secure', 2, flow_style="Sequence"))
        srv100.add_child(settings100)

        srv200 = SyntaxNode('srv-200', 3, is_block_sequence=True)
        settings200 = SyntaxNode('settings', 4)
        settings200.add_child(SyntaxNode('reliable', 4, flow_style="Sequence"))
        settings200.add_child(SyntaxNode('scalable', 4, flow_style="Sequence"))
        srv200.add_child(settings200)
        backup_to = SyntaxNode('backup_to', 5)
        srv200.add_child(backup_to)
        backup_to.add_child(SyntaxNode('storageUnit', 5, is_map_value="True"))

        server_config.add_child(srv100)
        server_config.add_child(srv200)

        database = SyntaxNode('database', 6, is_block_sequence=True)
        srv300 = SyntaxNode('srv-300', 7, is_block_sequence=True)
        database.add_child(srv300)

        webApp = SyntaxNode('webApp', 8, is_block_sequence=True)

        expected = [server_config, database, webApp]
        self.assertEqual(expected, parsed_yaml)

    def test_parse_valid_sequence_nested_mapping_yaml2(self):
        yaml_content = self.load_yaml_sample("valid2.yaml")
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        apiVersion = SyntaxNode('apiVersion', 0)
        apiVersion.add_child(SyntaxNode('v1', 0))
        kind = SyntaxNode('kind', 1)
        kind.add_child(SyntaxNode('Pod', 1))
        metadata = SyntaxNode('metadata', 2)
        name = SyntaxNode('name', 3)
        name.add_child(SyntaxNode('apache-pod', 3))
        labels = SyntaxNode('labels', 4)
        app = SyntaxNode('app', 5)
        app.add_child(SyntaxNode('web', 5))
        steps = SyntaxNode('steps', 6)
        step1 = SyntaxNode('uses', 7, is_block_sequence=True)
        step1.add_child(SyntaxNode('actions/checkout@v2', 7))
        step2 = SyntaxNode('name', 8, is_block_sequence=True)
        step2.add_child(SyntaxNode('Set up Python', 8))
        steps.add_child(step1)
        steps.add_child(step2)
        labels.add_child(app)
        labels.add_child(steps)
        metadata.add_child(name)
        metadata.add_child(labels)

        expected = [apiVersion, kind, metadata]
        self.assertEqual(expected, parsed_yaml)

    def test_parse_valid_sequence_nested_mapping_yaml3(self):
        yaml_content = self.load_yaml_sample("valid3.yaml")
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        kind = SyntaxNode('kind', 2)
        kind.add_child(SyntaxNode('Pod', 2))
        metadata = SyntaxNode('metadata', 3)
        build = SyntaxNode('build', 5)
        build.add_child(SyntaxNode('"2020-01-01"', 5))
        resources = SyntaxNode('resources', 6)
        emptyLabel = SyntaxNode('emptyLabel', 8)
        metadata.add_child(build)
        metadata.add_child(resources)
        metadata.add_child(emptyLabel)

        expected = [kind, metadata]
        self.assertEqual(expected, parsed_yaml)


if __name__ == '__main__':
    unittest.main()

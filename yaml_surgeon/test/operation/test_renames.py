import unittest
from yaml_surgeon.yaml_lexer import scan_text
from yaml_surgeon.yaml_parser import parse_line_tokens
from yaml_surgeon.yaml_operation import YamlOperation


class TestRenames(unittest.TestCase):

    def test_node_rename_key(self):
        yaml_content = """
            - parent1:
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
        YamlOperation(yaml_content).named('srv-100').rename('renamed-srv-100').execute()
        for node in parsed_yaml:
            if node.name == 'renamed-srv-100':
                self.assertIn('renamed-srv-100', node.name)

    def test_rename_value(self):
        yaml_content = """
            - parent1:
                - srv-100:
                    fast: true
                - srv-200"""
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)
        output_yaml = YamlOperation(parsed_yaml, lexed_lines).named('true').rename('false').execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - parent1:
                - srv-100:
                    fast: false
                - srv-200"""
        self.assertEqual(expected_yaml_content, output_yaml_string)

    def test_rename_flow_sequence(self):
        yaml_content = """
            - spam:
                - bacon: [egg, spam]"""
        output_yaml = YamlOperation(yaml_content).named('egg').rename('ham').execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - spam:
                - bacon: [ham, spam]"""
        self.assertEqual(expected_yaml_content, output_yaml_string)

    def test_rename_flow_mapping(self):
        yaml_content = """
            - sausage:
                - bacon: {egg: spam} # Hello"""
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)
        output_yaml = YamlOperation(parsed_yaml, lexed_lines).named('egg').rename('ham').execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - sausage:
                - bacon: {ham: spam} # Hello"""
        self.assertEqual(expected_yaml_content, output_yaml_string)


if __name__ == '__main__':
    unittest.main()

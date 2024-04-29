import unittest
from yaml_surgeon.yaml_lexer import scan_text
from yaml_surgeon.yaml_parser import parse_line_tokens
from yaml_surgeon.yaml_operation import YamlOperation


class TestInsert(unittest.TestCase):

    def test_node_insert_sibling_line(self):
        yaml_content = """
            - parent1:
                - srv-100:
                    fast: true"""
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)
        output_yaml = YamlOperation(parsed_yaml, lexed_lines).named('srv-100').insert_sibling('srv-200').execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - parent1:
                - srv-100:
                    fast: true
                - srv-200"""
        self.assertEqual(expected_yaml_content, output_yaml_string,
                         "The output YAML should match the expected content including insertion")

    def test_node_insert_sibling_flow_sequence(self):
        yaml_content = """
            - sausage:
                - bacon: [egg, spam]"""
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)
        output_yaml = YamlOperation(parsed_yaml, lexed_lines).named('spam').insert_sibling('ham').execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - sausage:
                - bacon: [egg, spam, ham]"""
        self.assertEqual(expected_yaml_content, output_yaml_string,
                         "The output YAML should match the expected content including insertion")

    def test_node_insert_sibling_flow_style_mapping(self):
        yaml_content = """
            - sausage:
                - bacon: {egg: spam} # Hello"""
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)
        output_yaml = YamlOperation(parsed_yaml, lexed_lines).named('egg').insert_sibling('ham').execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - sausage:
                - bacon: {egg: spam, ham:} # Hello"""
        self.assertEqual(expected_yaml_content, output_yaml_string,
                         "The output YAML should match the expected content including insertion")


if __name__ == '__main__':
    unittest.main()

import unittest
from yaml_surgeon.yaml_lexer import scan_text
from yaml_surgeon.yaml_parser import parse_line_tokens
from yaml_surgeon.yaml_operation import YamlOperation


class TestDuplicate(unittest.TestCase):

    def test_node_duplicate_single(self):
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
        output_yaml = YamlOperation(yaml_content).named('srv-100').with_parents("parent1").duplicate_as("duplicate-srv-100").execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - parent1:
                - srv-100:
                    fast: true
                - duplicate-srv-100:
                    fast: true
            - parent2:
                - srv-100:
                    secure: true
            - database:
                - srv-300
            - webApp"""
        self.assertEqual(expected_yaml_content, output_yaml_string,
                         "The output YAML should match the expected content with duplicates")

    def test_node_duplicate_multiple(self):
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
        output_yaml = YamlOperation(yaml_content).named('srv-100').duplicate_as("duplicate-srv-100").execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - parent1:
                - srv-100:
                    fast: true
                - duplicate-srv-100:
                    fast: true
            - parent2:
                - srv-100:
                    secure: true
                - duplicate-srv-100:
                    secure: true
            - database:
                - srv-300
            - webApp"""
        self.assertEqual(expected_yaml_content, output_yaml_string,
                         "The output YAML should match the expected content with duplicates")

    def test_node_duplicate_more_types(self):
        yaml_content = """
            - spam:
                - egg: true
                - ham:
                    # Lovely
                    - spam
                - bacon: [egg, spam]
            - sausage:
                - bacon: [egg, spam]
                - beans: {spam: spam}"""
        output_yaml = YamlOperation(yaml_content).named('bacon').with_parents('spam').duplicate_as('spam').execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - spam:
                - egg: true
                - ham:
                    # Lovely
                    - spam
                - bacon: [egg, spam]
                - spam: [egg, spam]
            - sausage:
                - bacon: [egg, spam]
                - beans: {spam: spam}"""
        self.assertEqual(expected_yaml_content, output_yaml_string,
                         "The output YAML should match the expected content with duplicates")

    def test_node_duplicate_flow_sequence(self):
        yaml_content = """
            - spam:
                - bacon: [egg, spam]"""
        output_yaml = YamlOperation(yaml_content).named('egg').with_parents('bacon').duplicate_as('ham').execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - spam:
                - bacon: [egg, ham, spam]"""
        self.assertEqual(expected_yaml_content, output_yaml_string,
                         "The output YAML should match the expected content")

    def test_node_duplicate_flow_style_mapping(self):
        yaml_content = """
            - sausage:
                - bacon: {egg: spam} # Hello"""
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)
        output_yaml = YamlOperation(parsed_yaml, lexed_lines).named('egg').duplicate_as('ham').execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - sausage:
                - bacon: {egg: spam, ham: spam} # Hello"""
        self.assertEqual(expected_yaml_content, output_yaml_string,
                         "The output YAML should match the expected content including insertion")


if __name__ == '__main__':
    unittest.main()
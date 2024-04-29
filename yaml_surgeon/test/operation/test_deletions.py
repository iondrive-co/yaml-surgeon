import unittest
from yaml_surgeon.yaml_lexer import scan_text
from yaml_surgeon.yaml_parser import parse_line_tokens
from yaml_surgeon.yaml_operation import YamlOperation


class TestDeletions(unittest.TestCase):

    def test_node_rename(self):
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

    def test_node_delete(self):
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
        YamlOperation(parsed_yaml, lexed_lines).named('srv-100').delete().execute()
        for node in parsed_yaml:
            self.assertNotEqual(node.name, 'srv-100', "Node 'srv-100' should have been deleted")

    def test_node_delete_flow_sequence(self):
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
        output_yaml = YamlOperation(yaml_content).named('egg').delete().execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - spam:
                - ham:
                    # Lovely
                    - spam
                - bacon: [spam]
            - sausage:
                - bacon: [spam]
                - beans: {spam: spam}"""
        self.assertEqual(expected_yaml_content, output_yaml_string,
                         "The output YAML should match the expected content with duplicates")

    def test_node_delete_flow_mapping_key(self):
        yaml_content = """
            - spam:
                - egg: true
                - ham:
                    # Lovely
                    - spam
                - bacon: [egg, spam]
            - sausage:
                - bacon: [egg, spam]
                - beans: {ham: spam}"""
        output_yaml = YamlOperation(yaml_content).named('ham').with_parents('beans').delete().execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - spam:
                - egg: true
                - ham:
                    # Lovely
                    - spam
                - bacon: [egg, spam]
            - sausage:
                - bacon: [egg, spam]
                - beans: {}"""
        self.assertEqual(expected_yaml_content, output_yaml_string)

    def test_node_delete_flow_mapping_value(self):
        yaml_content = """
            - spam:
                - egg: true
                - ham:
                    # Lovely
                    - spam
                - bacon: [egg, spam]
            - sausage:
                - bacon: [egg, spam]
                - beans: {ham: spam}"""
        output_yaml = YamlOperation(yaml_content).named('spam').with_parent_at_level('ham', 2).delete().execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - spam:
                - egg: true
                - ham:
                    # Lovely
                    - spam
                - bacon: [egg, spam]
            - sausage:
                - bacon: [egg, spam]
                - beans: {ham: }"""
        self.assertEqual(expected_yaml_content, output_yaml_string)


if __name__ == '__main__':
    unittest.main()
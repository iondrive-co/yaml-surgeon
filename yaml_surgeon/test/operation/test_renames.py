import unittest
from yaml_surgeon.yaml_lexer import scan_text
from yaml_surgeon.yaml_parser import parse_line_tokens
from yaml_surgeon.yaml_operation import YamlOperation


class TestRenames(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
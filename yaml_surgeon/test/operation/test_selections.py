import unittest
from yaml_surgeon.yaml_lexer import scan_text
from yaml_surgeon.yaml_parser import parse_line_tokens
from yaml_surgeon.yaml_operation import YamlOperation


class TestYamlOperationSelections(unittest.TestCase):

    def test_node_selection(self):
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
        selected_nodes = YamlOperation(parsed_yaml, lexed_lines).named('srv-100').get_selected_nodes()
        self.assertEqual(len(selected_nodes), 2)
        self.assertEqual(selected_nodes[0].name, 'srv-100', 'srv-100')

        selected_nodes = YamlOperation(parsed_yaml, lexed_lines).named('srv-100').with_parents('parent2').get_selected_nodes()
        self.assertEqual(len(selected_nodes), 1)
        self.assertEqual(selected_nodes[0].name, 'srv-100')
        child_names = [child.name for child in selected_nodes[0].children]
        self.assertIn('secure', child_names)

    def test_node_multi_selection(self):
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
        selected_nodes = YamlOperation(parsed_yaml, lexed_lines).named('srv-100', 'srv-300').get_selected_nodes()
        self.assertEqual(len(selected_nodes), 3)
        self.assertEqual(selected_nodes[0].name, 'srv-100', 'srv-100')
        self.assertEqual(selected_nodes[1].name, 'srv-100', 'srv-100')
        self.assertEqual(selected_nodes[2].name, 'srv-300', 'srv-300')

    def test_node_multi_parent_selection(self):
        yaml_content = """
        - parent1:
            - srv-100:
                fast: true
        - parent2:
            - srv-100:
                secure: true
        - parent3:
            - srv-100
        - webApp"""
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)
        selected_nodes = YamlOperation(parsed_yaml, lexed_lines)\
            .named('srv-100').with_parents('parent1', 'parent2').get_selected_nodes()
        self.assertEqual(len(selected_nodes), 2)
        self.assertEqual(selected_nodes[0].name, 'srv-100', 'srv-100')
        self.assertEqual(selected_nodes[1].name, 'srv-100', 'srv-100')

    def test_node_contains_selection(self):
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
        selected_nodes = YamlOperation(parsed_yaml, lexed_lines).name_contains('srv').get_selected_nodes()
        self.assertEqual(len(selected_nodes), 3)
        self.assertEqual(selected_nodes[0].name, 'srv-100', 'srv-100')
        self.assertEqual(selected_nodes[1].name, 'srv-100', 'srv-100')
        self.assertEqual(selected_nodes[2].name, 'srv-300', 'srv-300')

    def test_node_select_level(self):
        yaml_content = """
            - spam:
                - egg: true
                - ham:
                    # Lovely
                    - spam"""
        selected_nodes = YamlOperation(yaml_content).named_at_level('spam', 2).get_selected_nodes()
        self.assertEqual(len(selected_nodes), 1)
        self.assertEqual(selected_nodes[0].start_line_number, 5)

    def test_chain_multiple(self):
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
        output_yaml = YamlOperation(yaml_content).named('bacon').with_parents('spam').duplicate_as('can').then()\
                                                 .named('egg').with_parents('can').duplicate_as('spam').execute()
        output_yaml_string = "\n".join(output_yaml)
        expected_yaml_content = """
            - spam:
                - egg: true
                - ham:
                    # Lovely
                    - spam
                - bacon: [egg, spam]
                - can: [egg, spam, spam]
            - sausage:
                - bacon: [egg, spam]
                - beans: {spam: spam}"""
        self.assertEqual(expected_yaml_content, output_yaml_string,
                         "The output YAML should match the expected content with duplicates")


if __name__ == '__main__':
    unittest.main()
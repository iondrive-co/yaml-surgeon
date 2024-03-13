import unittest
from yaml_surgeon.yaml_lexer import scan_text
from yaml_surgeon.yaml_parser import parse_line_tokens
from yaml_surgeon.yaml_operation import find_children_of_node_called, YamlOperation, create_line_number_map
from yaml_surgeon.structures import SyntaxNode


class TestFindChildren(unittest.TestCase):

    @staticmethod
    def load_yaml_sample(file_name):
        with open("../samples/" + file_name, 'r') as file:
            text = file.read()
        return text

    def test_find_children_of_node_valid_list_nested_dict(self):
        yaml_content = self.load_yaml_sample("valid1.yaml")
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        result = find_children_of_node_called(parsed_yaml, 'settings')
        expected = [SyntaxNode('fast', 2), SyntaxNode('secure', 2), SyntaxNode('reliable', 4), SyntaxNode('scalable', 4)]
        assert_syntax_nodes_equal(expected, result)

        result_level = find_children_of_node_called(parsed_yaml, 'serverConfig', 0)
        expected = [SyntaxNode('srv-100', 1), SyntaxNode('srv-200', 3)]
        assert_syntax_nodes_equal(expected, result_level)

    def test_find_children_of_node_valid_list_nested_dict_yaml2(self):
        yaml_content = self.load_yaml_sample("valid2.yaml")
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        result = find_children_of_node_called(parsed_yaml, 'labels')
        expected = [SyntaxNode('app', 5), SyntaxNode('steps', 6)]
        assert_syntax_nodes_equal(expected, result)

        result_level = find_children_of_node_called(parsed_yaml, 'metadata', 0)
        expected = [SyntaxNode('name', 3), SyntaxNode('labels', 4)]
        assert_syntax_nodes_equal(expected, result_level)

    def test_find_children_of_node_valid_list_nested_dict_yaml3(self):
        yaml_content = self.load_yaml_sample("valid3.yaml")
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)

        result = find_children_of_node_called(parsed_yaml, 'metadata')
        expected = [SyntaxNode('build', 5), SyntaxNode('resources', 6), SyntaxNode('emptyLabel', 8)]
        assert_syntax_nodes_equal(expected, result)

        result_level = find_children_of_node_called(parsed_yaml, 'kind', 0)
        expected = [SyntaxNode('Pod', 2)]
        assert_syntax_nodes_equal(expected, result_level)


def assert_syntax_nodes_equal(expected, actual):
    assert len(expected) == len(actual), f"Expected {len(expected)} nodes, found {len(actual)} nodes"
    for exp_node, act_node in zip(expected, actual):
        assert exp_node.name == act_node.name, f"Expected node name '{exp_node.name}', found '{act_node.name}'"


class TestYamlOperation(unittest.TestCase):

    def test_node_selection(self):
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
        selected_nodes = YamlOperation(parsed_yaml, lexed_lines).named('srv-100').get_selected_nodes()
        self.assertEqual(len(selected_nodes), 2)
        self.assertEqual(selected_nodes[0].name, 'srv-100', 'srv-100')

        selected_nodes = YamlOperation(parsed_yaml, lexed_lines).named('srv-100').with_parent('parent2').get_selected_nodes()
        self.assertEqual(len(selected_nodes), 1)
        self.assertEqual(selected_nodes[0].name, 'srv-100')
        child_names = [child.name for child in selected_nodes[0].children]
        self.assertIn('secure', child_names)

    def test_node_rename(self):
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
        YamlOperation(yaml_content).named('srv-100').rename('renamed-srv-100').execute()
        for node in parsed_yaml:
            if node.name == 'renamed-srv-100':
                self.assertIn('renamed-srv-100', node.name)

    def test_node_delete(self):
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
        YamlOperation(parsed_yaml, lexed_lines).named('srv-100').delete().execute()
        for node in parsed_yaml:
            self.assertNotEqual(node.name, 'srv-100', "Node 'srv-100' should have been deleted")

    def test_node_delete_flow(self):
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
        output_yaml = YamlOperation(yaml_content).named('srv-100').with_parent("parent1").duplicate_as("duplicate-srv-100").execute()
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
        output_yaml = YamlOperation(yaml_content).named('bacon').with_parent('spam').duplicate_as('spam').execute()
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
        output_yaml = YamlOperation(yaml_content).named('bacon').with_parent('spam').duplicate_as('can').then()\
                                                 .named('egg').with_parent('can').duplicate_as('spam').execute()
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


class TestHelperFunctions(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()

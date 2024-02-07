import unittest
from yaml_lexer import scan_text, AlphaSpansStateMachine
from structures import Line


class TestYamlLineSplitting(unittest.TestCase):
    sm = AlphaSpansStateMachine()

    def test_empty_line(self):
        line = ""
        expected = [""]
        self.assertEqual(expected, self.sm.parse(line))

    def test_unquoted_quoted_string(self):
        line = "Hello, 'world! This is a test.' (StateMachine)"
        expected = ["Hello", ", ", "'world! This is a test.'", " (", "StateMachine", ")"]
        self.assertEqual(expected, self.sm.parse(line))

    def test_array(self):
        line =      "        settings: []"
        expected = ["        ", "settings", ": []"]
        self.assertEqual(expected, self.sm.parse(line))

    def test_nested_array(self):
        line =      "        settings: [fast, secure ]"
        expected = ["        ", "settings", ": [", "fast", ", ", "secure", " ]"]
        self.assertEqual(expected, self.sm.parse(line))

    def test_nested_array_with_quotes(self):
        line = '        settings2: [ "fast:", "secure"]'
        expected = ["        ", "settings2", ": [ ", '"fast:"', ', ', '"secure"', ']']
        self.assertEqual(expected, self.sm.parse(line))

    def test_nested_dict(self):
        line = "        bob: {charlie: 3, d: 4}"
        expected = ["        ", "bob", ": {", "charlie", ": ", "3", ", ", "d", ": ", "4", "}"]
        self.assertEqual(expected, self.sm.parse(line))

    def test_comment(self):
        line = "# Document start"
        expected = ["# ", "Document start"]
        self.assertEqual(expected, self.sm.parse(line))


class TestLexYaml(unittest.TestCase):

    @staticmethod
    def load_yaml_samples(file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        samples = text.split('[yaml')
        return {f"yaml{i}": sample.split(']', 1)[1].strip() for i, sample in enumerate(samples) if sample.strip()}

    def test_lex_valid_list_nested_dict(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml1"]
        parsed_yaml = scan_text(yaml_content)
        expected = [
            Line(text_elements=["- ", "serverConfig", ":"], line_number=1, level=0),
            Line(text_elements=["    - ", "srv-100", ":"], line_number=2, level=1),
            Line(text_elements=["        ", "settings", ": [", "fast", ", ", "secure", "]"], line_number=3, level=2),
            Line(text_elements=["    - ", "srv-200", ":"], line_number=4, level=1),
            Line(text_elements=["        ", "settings", ": [", "reliable", ", ", "scalable", "]"], line_number=5,
                 level=2),
            Line(text_elements=["        ", "backup_to", ": ", "storageUnit"], line_number=6, level=2),
            Line(text_elements=["- ", "database", ":"], line_number=7, level=0),
            Line(text_elements=["    - ", "srv-300"], line_number=8, level=1),
            Line(text_elements=["- ", "webApp"], line_number=9, level=0),
        ]
        self.assertEqual(expected, parsed_yaml)

    def test_lex_valid_dict_nested_list(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml2"]
        parsed_yaml = scan_text(yaml_content)
        expected = [
            Line(text_elements=['apiVersion', ': ', 'v1'], line_number=1, level=0),
            Line(text_elements=['kind', ': ', 'Pod'], line_number=2, level=0),
            Line(text_elements=['metadata', ':'], line_number=3, level=0),
            Line(text_elements=[' ', 'name', ': ', 'apache-pod'], line_number=4, level=1),
            Line(text_elements=[' ', 'labels', ':'], line_number=5, level=1),
            Line(text_elements=['   ', 'app', ': ', 'web'], line_number=6, level=2),
            Line(text_elements=['   ', 'steps', ':'], line_number=7, level=2),
            Line(text_elements=['     - ', 'uses', ': ', 'actions/checkout@v2'], line_number=8, level=3),
            Line(text_elements=['     - ', 'name', ': ', 'Set up Python'], line_number=9, level=3),
            Line(text_elements=['...'], line_number=10, level=0)
        ]
        self.assertEqual(expected, parsed_yaml)

    def test_lex_valid_awkward_comments_and_spaces(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml3"]
        parsed_yaml = scan_text(yaml_content)
        expected = [
            Line(text_elements=["...", ], line_number=1, level=0),
            Line(text_elements=["# ", "Document start"], line_number=2, level=0),
            Line(text_elements=["kind", ": ", "Pod # Comment at line end"], line_number=3, level=0),
            Line(text_elements=["metadata", ":"], line_number=4, level=0),
            Line(text_elements=["  # ", "A comment line"], line_number=5, level=1),
            Line(text_elements=["  ", "build", ": ", "\"2020-01-01\""], line_number=6, level=1),
            Line(text_elements=["  ", "resources", ":"], line_number=7, level=1),
            Line(text_elements=["    # ", "Nothing here but a comment"], line_number=8, level=2),
            Line(text_elements=["  ", "emptyLabel", ": {}"], line_number=9, level=1)
        ]
        self.assertEqual(expected, parsed_yaml)


if __name__ == '__main__':
    unittest.main()

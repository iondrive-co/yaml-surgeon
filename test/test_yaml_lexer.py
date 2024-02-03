import unittest
from yaml_lexer import scan_text, split_nested_structures
from structures import Line


class TestYamlLineSplitting(unittest.TestCase):
    def test_empty_line(self):
        line = ""
        expected = [""]
        self.assertEqual(expected, split_nested_structures(line))

    def test_nested_array(self):
        line =      "        settings: [fast, secure ]"
        expected = ["        settings: [", "fast", ", ", "secure", " ]"]
        self.assertEqual(expected, split_nested_structures(line))

    def test_nested_array_with_quotes(self):
        line = '        settings2: [ "fast", "secure"]'
        expected = ['        settings2: [ ', '"fast"', ', ', '"secure"', ']']
        self.assertEqual(expected, split_nested_structures(line))

    def test_nested_dict(self):
        line = "        bob: {charlie: 3, d: 4}"
        expected = ["        bob: {", "charlie", ": ", "3", ", ", "d", ": ", "4", "}"]
        self.assertEqual(expected, split_nested_structures(line))


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
            Line("- serverConfig:", 1, 0),
            Line("    - srv-100:", 2, 1),
            Line("        settings: [fast, secure]", 3, 2),
            Line("    - srv-200:", 4, 1),
            Line("        settings: [reliable, scalable]", 5, 2),
            Line("        backup_to: storageUnit", 6, 2),
            Line("- database:", 7, 0),
            Line("    - srv-300", 8, 1),
            Line("- webApp", 9, 0)
        ]
        self.assertEqual(expected, parsed_yaml)

    def test_lex_valid_dict_nested_list(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml2"]
        parsed_yaml = scan_text(yaml_content)
        expected = [
            Line("apiVersion: v1", 1, 0),
            Line("kind: Pod", 2, 0),
            Line("metadata:", 3, 0),
            Line(" name: apache-pod", 4, 1),
            Line(" labels:", 5, 1),
            Line("   app: web", 6, 2),
            Line("   steps:", 7, 2),
            Line("     - uses: actions/checkout@v2", 8, 3),
            Line("     - name: Set up Python", 9, 3),
            Line("...", 10, 0)
        ]
        self.assertEqual(expected, parsed_yaml)

    def test_lex_valid_awkward_comments_and_spaces(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml3"]
        parsed_yaml = scan_text(yaml_content)
        expected = [
            Line("...", 1, 0),
            Line("# Document start", 2, 0),
            Line("kind: Pod # Comment at line end", 3, 0),
            Line("metadata:", 4, 0),
            Line("  # A comment line", 5, 1),
            Line("  build: \"2020-01-01\"", 6, 1),
            Line("  resources:", 7, 1),
            Line("    # Nothing here but a comment", 8, 2),
            Line("  emptyLabel: {}", 9, 1)
        ]
        self.assertEqual(expected, parsed_yaml)


if __name__ == '__main__':
    unittest.main()
import unittest
from yaml_lexer import scan_text
from structures import Line


class TestLexYaml(unittest.TestCase):

    @staticmethod
    def load_yaml_samples(file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        samples = text.split('[yaml')
        return {f"yaml{i}": sample.split(']', 1)[1].strip() for i, sample in enumerate(samples) if sample.strip()}

    def test_yaml1(self):
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

    def test_yaml2(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml2"]
        parsed_yaml = scan_text(yaml_content)
        expected = [
            Line("apiVersion: v1", 1, 0),
            Line("kind: Pod", 2, 0),
            Line("metadata:", 3, 0),
            Line(" name: apache-pod", 4, 1),
            Line(" labels:", 5, 1),
            Line("   app: web", 6, 2)
        ]
        self.assertEqual(expected, parsed_yaml)

    def test_yaml3(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml3"]
        parsed_yaml = scan_text(yaml_content)
        expected = [
            Line("...", 1, 0),
            Line("jobs:", 2, 0),
            Line("  blueberry:", 3, 1),
            Line("    runs-on: ubuntu-latest", 4, 2),
            Line("    steps:", 5, 2),
            Line("    - uses: actions/checkout@v2", 6, 2),
            Line("    - name: Set up Python", 7, 2),
            Line("...", 8, 0)
        ]
        self.assertEqual(expected, parsed_yaml)


if __name__ == '__main__':
    unittest.main()
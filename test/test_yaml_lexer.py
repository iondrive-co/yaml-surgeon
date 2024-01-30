import unittest
from yaml_lexer import scan_text
from structures import YamlLine


class TestLexYaml(unittest.TestCase):

    @staticmethod
    def load_yaml_samples(file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        samples = text.split('[yaml')
        return {f"yaml{i}": sample.split(']', 1)[1].strip() for i, sample in enumerate(samples) if sample.strip()}

    def test_yaml1(self):
        yaml_content = self.load_yaml_samples("yaml_samples.txt")["yaml1"]
        parsed_yaml = scan_text(yaml_content)
        expected = [
            YamlLine("- serverConfig:", 1, 0),
            YamlLine("    - srv-100:", 2, 1),
            YamlLine("        settings: [fast, secure]", 3, 2),
            YamlLine("    - srv-200:", 4, 1),
            YamlLine("        settings: [reliable, scalable]", 5, 2),
            YamlLine("        backup_to: storageUnit", 6, 2),
            YamlLine("- database:", 7, 0),
            YamlLine("    - srv-300", 8, 1),
            YamlLine("- webApp", 9, 0)
        ]
        self.assertEqual(expected, parsed_yaml)

    def test_yaml2(self):
        yaml_content = self.load_yaml_samples("yaml_samples.txt")["yaml2"]
        parsed_yaml = scan_text(yaml_content)
        expected = [
            YamlLine("apiVersion: v1", 1, 0),
            YamlLine("kind: Pod", 2, 0),
            YamlLine("metadata:", 3, 0),
            YamlLine(" name: apache-pod", 4, 1),
            YamlLine(" labels:", 5, 1),
            YamlLine("   app: web", 6, 2)
        ]
        self.assertEqual(expected, parsed_yaml)

    def test_yaml3(self):
        yaml_content = self.load_yaml_samples("yaml_samples.txt")["yaml3"]
        parsed_yaml = scan_text(yaml_content)
        expected = [
            YamlLine("...", 1, 0),
            YamlLine("jobs:", 2, 0),
            YamlLine("  blueberry:", 3, 1),
            YamlLine("    runs-on: ubuntu-latest", 4, 2),
            YamlLine("    steps:", 5, 2),
            YamlLine("    - uses: actions/checkout@v2", 6, 2),
            YamlLine("    - name: Set up Python", 7, 2),
            YamlLine("...", 8, 0)
        ]
        self.assertEqual(expected, parsed_yaml)


if __name__ == '__main__':
    unittest.main()
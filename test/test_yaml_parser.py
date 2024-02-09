import unittest
from yaml_lexer import scan_text
from yaml_parser import parse_line_tokens
from structures import SyntaxNode


class TestParseYaml(unittest.TestCase):

    @staticmethod
    def load_yaml_samples(file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        samples = text.split('[yaml')
        return {f"yaml{i}": sample.split(']', 1)[1].strip() for i, sample in enumerate(samples) if sample.strip()}

    def test_parse_valid_list_nested_dict(self):
        yaml_content = self.load_yaml_samples("valid_yaml_samples.txt")["yaml1"]
        lexed_lines = scan_text(yaml_content)
        parsed_yaml = parse_line_tokens(lexed_lines)
        expected = [
            SyntaxNode(name='serverConfig', children=[
                SyntaxNode(name='srv-100', children=[
                    SyntaxNode(name='settings', children=[
                        SyntaxNode(name='fast', children=[]),
                        SyntaxNode(name='secure', children=[])
                    ])
                ]),
                SyntaxNode(name='srv-200', children=[
                    SyntaxNode(name='settings', children=[
                        SyntaxNode(name='reliable', children=[]),
                        SyntaxNode(name='scalable', children=[])
                    ]),
                    SyntaxNode(name='backup_to', children=[]),
                    SyntaxNode(name='storageUnit', children=[])
                ])
            ]),
            SyntaxNode(name='database', children=[
                SyntaxNode(name='srv-300', children=[])
            ]),
            SyntaxNode(name='webApp', children=[])
        ]
        self.assertEqual(expected, parsed_yaml)


if __name__ == '__main__':
    unittest.main()

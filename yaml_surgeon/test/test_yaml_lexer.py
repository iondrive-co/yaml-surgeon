import unittest
from yaml_surgeon.yaml_lexer import scan_text, AlphaSpansStateMachine
from yaml_surgeon.structures import Line, Token


class TestYamlLineSplitting(unittest.TestCase):
    sm = AlphaSpansStateMachine()

    def test_empty_line(self):
        line = ""
        expected = [Token(value='', types=[])]
        self.assertEqual(expected, self.sm.parse(line))

    def test_unquoted_quoted_string(self):
        line = "I Yam, 'what I yam.' (l)"
        expected = [
            Token(value='I Yam', types=['Scalar']),
            Token(value=', ', types=[]),
            Token(value="'what I yam.'", types=['Scalar']),
            Token(value=' (', types=[]),
            Token(value='l', types=['Scalar']),
            Token(value=')', types=[])
        ]
        self.assertEqual(expected, self.sm.parse(line))

    def test_list(self):
        line =      "        settings: []"
        expected = [Token(value='        ', types=[]),
                    Token(value='settings', types=['Scalar']),
                    Token(value=': []', types=['Dict', 'List'])]
        self.assertEqual(expected, self.sm.parse(line))

    def test_nested_list(self):
        line = "        settings: [fast, secure ]"
        expected = [
            Token(value='        ', types=[]),
            Token(value='settings', types=['Scalar']),
            Token(value=': [', types=['Dict', 'List']),
            Token(value='fast', types=['Scalar']),
            Token(value=', ', types=[]),
            Token(value='secure', types=['Scalar']),
            Token(value=' ]', types=[])
        ]
        self.assertEqual(expected, self.sm.parse(line))

    def test_nested_list_with_quotes(self):
        line = '        settings2: [ "fast:", "secure"]'
        expected = [
            Token(value='        ', types=[]),
            Token(value='settings2', types=['Scalar']),
            Token(value=': [ ', types=['Dict', 'List']),
            Token(value='"fast:"', types=['Scalar']),
            Token(value=', ', types=[]),
            Token(value='"secure"', types=['Scalar']),
            Token(value=']', types=[])
        ]
        self.assertEqual(expected, self.sm.parse(line))

    def test_nested_dict(self):
        line = "        bob: {charlie: 3, d: 4}"
        expected = [
            Token(value='        ', types=[]),
            Token(value='bob', types=['Scalar']),
            Token(value=': {', types=['Dict', 'Dict']),
            Token(value='charlie', types=['Scalar']),
            Token(value=': ', types=['Dict']),
            Token(value='3', types=['Scalar']),
            Token(value=', ', types=[]),
            Token(value='d', types=['Scalar']),
            Token(value=': ', types=['Dict']),
            Token(value='4', types=['Scalar']),
            Token(value='}', types=[])
        ]
        self.assertEqual(expected, self.sm.parse(line))

    def test_comment(self):
        line = "# Document start"
        expected = [
            Token(value='# Document start', types=['Comment'])
        ]
        self.assertEqual(expected, self.sm.parse(line))


class TestLexYaml(unittest.TestCase):

    @staticmethod
    def load_yaml_sample(file_name):
        with open("../samples/" + file_name, 'r') as file:
            text = file.read()
        return text

    def test_lex_valid_list_nested_dict(self):
        yaml_content = self.load_yaml_sample("valid1.yaml")
        parsed_yaml = scan_text(yaml_content)
        expected = [
            Line(tokens=[
                Token(value='- ', types=['List']),
                Token(value='serverConfig', types=['Scalar']),
                Token(value=':', types=['Dict'])
            ], line_number=1, level=0),
            Line(tokens=[
                Token(value='    - ', types=['List']),
                Token(value='srv-100', types=['Scalar']),
                Token(value=':', types=['Dict'])
            ], line_number=2, level=1),
            Line(tokens=[
                Token(value='        ', types=[]),
                Token(value='settings', types=['Scalar']),
                Token(value=': [', types=['Dict', 'List']),
                Token(value='fast', types=['Scalar']),
                Token(value=', ', types=[]),
                Token(value='secure', types=['Scalar']),
                Token(value=']', types=[])
            ], line_number=3, level=2),
            Line(tokens=[
                Token(value='    - ', types=['List']),
                Token(value='srv-200', types=['Scalar']),
                Token(value=':', types=['Dict'])
            ], line_number=4, level=1),
            Line(tokens=[
                Token(value='        ', types=[]),
                Token(value='settings', types=['Scalar']),
                Token(value=': [', types=['Dict', 'List']),
                Token(value='reliable', types=['Scalar']),
                Token(value=', ', types=[]),
                Token(value='scalable', types=['Scalar']),
                Token(value=']', types=[])
            ], line_number=5, level=2),
            Line(tokens=[
                Token(value='        ', types=[]),
                Token(value='backup_to', types=['Scalar']),
                Token(value=': ', types=['Dict']),
                Token(value='storageUnit', types=['Scalar'])
            ], line_number=6, level=2),
            Line(tokens=[
                Token(value='- ', types=['List']),
                Token(value='database', types=['Scalar']),
                Token(value=':', types=['Dict'])
            ], line_number=7, level=0),
            Line(tokens=[
                Token(value='    - ', types=['List']),
                Token(value='srv-300', types=['Scalar'])
            ], line_number=8, level=1),
            Line(tokens=[
                Token(value='- ', types=['List']),
                Token(value='webApp', types=['Scalar'])
            ], line_number=9, level=0)
        ]
        self.assertEqual(expected, parsed_yaml)
        reconstructed = '\n'.join(''.join(token.value for token in line.tokens) for line in parsed_yaml)
        self.assertEqual(yaml_content.strip(), reconstructed.strip())

    def test_lex_valid_dict_nested_list(self):
        yaml_content = self.load_yaml_sample("valid2.yaml")
        parsed_yaml = scan_text(yaml_content)
        expected = [
            Line(tokens=[
                Token(value='apiVersion', types=['Scalar']),
                Token(value=': ', types=['Dict']),
                Token(value='v1', types=['Scalar'])
            ], line_number=1, level=0),
            Line(tokens=[
                Token(value='kind', types=['Scalar']),
                Token(value=': ', types=['Dict']),
                Token(value='Pod', types=['Scalar'])
            ], line_number=2, level=0),
            Line(tokens=[
                Token(value='metadata', types=['Scalar']),
                Token(value=':', types=['Dict'])
            ], line_number=3, level=0),
            Line(tokens=[
                Token(value=' ', types=[]),
                Token(value='name', types=['Scalar']),
                Token(value=': ', types=['Dict']),
                Token(value='apache-pod', types=['Scalar'])
            ], line_number=4, level=1),
            Line(tokens=[
                Token(value=' ', types=[]),
                Token(value='labels', types=['Scalar']),
                Token(value=':', types=['Dict'])
            ], line_number=5, level=1),
            Line(tokens=[
                Token(value='   ', types=[]),
                Token(value='app', types=['Scalar']),
                Token(value=': ', types=['Dict']),
                Token(value='web', types=['Scalar'])
            ], line_number=6, level=2),
            Line(tokens=[
                Token(value='   ', types=[]),
                Token(value='steps', types=['Scalar']),
                Token(value=':', types=['Dict'])
            ], line_number=7, level=2),
            Line(tokens=[
                Token(value='     - ', types=['List']),
                Token(value='uses', types=['Scalar']),
                Token(value=': ', types=['Dict']),
                Token(value='actions/checkout@v2', types=['Scalar'])
            ], line_number=8, level=3),
            Line(tokens=[
                Token(value='     - ', types=['List']),
                Token(value='name', types=['Scalar']),
                Token(value=': ', types=['Dict']),
                Token(value='Set up Python', types=['Scalar'])
            ], line_number=9, level=3),
            Line(tokens=[
                Token(value='...', types=[])
            ], line_number=10, level=0)
        ]
        self.assertEqual(expected, parsed_yaml)
        reconstructed = '\n'.join(''.join(token.value for token in line.tokens) for line in parsed_yaml)
        self.assertEqual(yaml_content.strip(), reconstructed.strip())

    def test_lex_valid_awkward_comments_and_spaces(self):
        yaml_content = self.load_yaml_sample("valid3.yaml")
        parsed_yaml = scan_text(yaml_content)
        expected = [
            Line(tokens=[
                Token(value='...', types=[])
            ], line_number=1, level=0),
            Line(tokens=[
                Token(value='# Document start', types=['Comment']),
            ], line_number=2, level=0),
            Line(tokens=[
                Token(value='kind', types=['Scalar']),
                Token(value=': ', types=['Dict']),
                Token(value='Pod', types=['Scalar']),
                Token(value=' # Comment at line end', types=['Comment']),
            ], line_number=3, level=0),
            Line(tokens=[
                Token(value='metadata', types=['Scalar']),
                Token(value=':', types=['Dict'])
            ], line_number=4, level=0),
            Line(tokens=[
                Token(value='  ', types=[]),
                Token(value='# A common comment', types=['Comment']),
            ], line_number=5, level=1),
            Line(tokens=[
                Token(value='  ', types=[]),
                Token(value='build', types=['Scalar']),
                Token(value=': ', types=['Dict']),
                Token(value='"2020-01-01"', types=['Scalar'])
            ], line_number=6, level=1),
            Line(tokens=[
                Token(value='  ', types=[]),
                Token(value='resources', types=['Scalar']),
                Token(value=':', types=['Dict'])
            ], line_number=7, level=1),
            Line(tokens=[
                Token(value='    ', types=[]),
                Token(value="# No resources, but have another comment, it's only wafer-thin", types=['Comment'])
            ], line_number=8, level=2),
            Line(tokens=[
                Token(value='  ', types=[]),
                Token(value='emptyLabel', types=['Scalar']),
                Token(value=': {}', types=['Dict', 'Dict'])
            ], line_number=9, level=1)
        ]
        self.assertEqual(expected, parsed_yaml)
        reconstructed = '\n'.join(''.join(token.value for token in line.tokens) for line in parsed_yaml)
        self.assertEqual(yaml_content.strip(), reconstructed.strip())


if __name__ == '__main__':
    unittest.main()

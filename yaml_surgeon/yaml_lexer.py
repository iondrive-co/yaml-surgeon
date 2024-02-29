from yaml_surgeon.structures import Line, Token


class AlphaSpansStateMachine:

    # These characters end an unquoted alpha span
    terminating_chars = ':]},#'

    def __init__(self):
        self.state = 'Special'
        self.current_span = ''
        self.lookahead_span = ''
        self.spans = []
        self.start_quote = ''
        self.span_types = []

    def process(self, char):
        if self.state == 'Special':
            if char.isalnum():
                self._end_span()
                self.state = 'Alpha'
                self.span_types.append('Scalar')
            elif char in "'\"":
                self._end_span()
                self.start_quote = char
                self.state = 'Quoted Alpha'
                self.span_types.append('Scalar')
            else:
                if char in '-[':
                    self.span_types.append('List')
                elif char in ':{':
                    self.span_types.append('Dict')
                elif char == '#':
                    self._end_span()
                    # Treat this as a quoted alpha with no start, meaning take everything until the end of the line
                    self.start_quote = None
                    self.state = 'Quoted Alpha'
                    self.span_types.append('Comment')
            self.current_span += char
        elif self.state == 'Alpha':
            if char in self.terminating_chars:
                self._end_span()
                self.state = 'Special'
                if char == ':':
                    self.span_types.append('Dict')
                elif char == '#':
                    self.start_quote = None
                    self.state = 'Quoted Alpha'
                    self.span_types.append('Comment')
                self.current_span += char
            elif char.isalnum():
                self.current_span += char
            else:  # Other chars may be part of this span if more alpha are coming up
                self.state = 'AlphaOrSpecial'
                self.lookahead_span = char
        elif self.state == 'AlphaOrSpecial':
            if char in self.terminating_chars:
                self._end_span()
                self.state = 'Special'
                if char == ':':
                    self.span_types.append('Dict')
                elif char == '#':
                    self.start_quote = None
                    self.state = 'Quoted Alpha'
                    self.span_types.append('Comment')
                self.current_span += self.lookahead_span
                self.lookahead_span = ''
                self.current_span += char
            elif char.isalnum():
                self.current_span += self.lookahead_span
                self.lookahead_span = ''
                self.current_span += char
                self.state = 'Alpha'
            elif char in "'\"":
                # Put the lookahead span into a special span first
                self._end_span()
                self.current_span = self.lookahead_span
                self.lookahead_span = ''
                self._end_span()
                # Start a new quoted alpha span
                self.start_quote = char
                self.state = 'Quoted Alpha'
                self.current_span += char
            else:
                self.lookahead_span += char
        elif self.state == 'Quoted Alpha':
            if char == self.start_quote:
                # Include the quote in the current span
                self.current_span += char
                self._end_span()
                self.state = 'Special'
            else:
                self.current_span += char

    def _end_span(self):
        if self.current_span:
            self.spans.append(Token(self.current_span, self.span_types))
            self.current_span = ''
            self.span_types = []

    def parse(self, text):
        if not text:
            return [Token('', [])]
        for char in text:
            self.process(char)
        # Handle any remaining span when the end of the text is reached
        self._end_span()
        # If there was any lookahead span, that means it is a special span not connected to the previous alpha span
        if self.lookahead_span:
            self.current_span += self.lookahead_span
        self._end_span()
        # Clear state for next time
        spans_text = self.spans
        self.spans = []
        self.state = 'Special'
        return spans_text


sm = AlphaSpansStateMachine()


def scan_text(text):
    """
    Build an ordered list of Line objects from the specified text, including calculating the nesting level
    of each line. We preserve all data including spaces as we don't want to make any unnecessary modifications
    """
    lines = text.splitlines()
    if not lines:
        return []
    yaml_lines = []
    nesting_level = 0
    previous_indent = len(lines[0]) - len(lines[0].lstrip())
    block_indent_amounts = []
    for line_number, line in enumerate(lines):
        current_indent = len(line) - len(line.lstrip())
        if current_indent > previous_indent:
            block_indent_amounts.append(current_indent - previous_indent)
            nesting_level += 1
        elif current_indent < previous_indent:
            # We can unindent by one or more of the stacked block indent amounts
            indent_decrease = previous_indent - current_indent
            while indent_decrease > 0:
                if not block_indent_amounts:
                    raise SyntaxError(f"Indent to the left of the start on line {line_number}: {line}")
                indent_decrease -= block_indent_amounts.pop()
                nesting_level -= 1
        line_elements = sm.parse(line)
        yaml_lines.append(Line(line_elements, line_number + 1, nesting_level))
        previous_indent = current_indent
    return yaml_lines



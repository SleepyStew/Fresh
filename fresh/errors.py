from fresh.tokens import ERROR_KEYWORDS

ERROR_STRING_1 = "Expected " + ", ".join(ERROR_KEYWORDS) + ", return, continue, break, type int, float, string, list or identifier, or '+', '-', '*', '/', '^', '[', " \
                                                           "'(' or 'not'"
ERROR_STRING_2 = "Expected type int, float, string, list or identifier, or '+', '-', '*', '/', '^', '[', '(' or 'not'"

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'\nFile {self.pos_start.filename}, line {self.pos_start.line + 1}:{self.pos_start.column + 1}'
        result += '\nError occurred here:\n' + string_with_arrows(self.pos_start.filetext, self.pos_start, self.pos_end)
        return result


class IllegalCharacterError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'IllegalCharacterError', details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'InvalidSyntaxError', details)


class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'RuntimeError', details)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f'\n{self.error_name}: {self.details}'
        result += '\nError occurred here:\n' + string_with_arrows(self.pos_start.filetext, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        context = self.context
        contexts = []
        while context:
            contexts.append(f'\n    File {pos.filename}, line {pos.line + 1}:{pos.column + 1}, in {context.display_name}')
            pos = context.parent_entry_position
            context = context.parent
        contexts.reverse()
        result += ''.join(contexts)
        return 'Traceback (most recent call last):' + result


class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details, expected_char):
        super().__init__(pos_start, pos_end, 'ExpectedCharError', f"'{expected_char}' {details}")


# Error Arrows #


def string_with_arrows(text, pos_start, pos_end):
    result = ''

    # Calculate indices
    index_start = max(text.rfind('\n', 0, pos_start.index), 0)
    index_end = text.find('\n', index_start + 1)
    if index_end < 0: index_end = len(text)

    # Generate each line
    line_count = pos_end.line - pos_start.line + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[index_start:index_end]
        col_start = pos_start.column if i == 0 else 0
        col_end = pos_end.column if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        index_start = index_end
        index_end = text.find('\n', index_start + 1)
        if index_end < 0: index_end = len(text)

    return result.replace('\t', '')
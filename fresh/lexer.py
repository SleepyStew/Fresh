from fresh.constants import *
from fresh.errors import *
from fresh.tokens import *
from fresh.position import Position


class Lexer:
    def __init__(self, filename, text, debug):
        self.filename = filename
        self.text = text
        self.pos = Position(-1, 0, -1, filename, text)
        self.current_char = None
        self.debug = debug
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in ';\n':
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char in '"':
                token, error = self.make_string('"')
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char in "'":
                token, error = self.make_string("'")
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(self.make_minus_or_arrow())
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                token = self.make_comment_or_div()
                if token is not None:
                    tokens.append(token)
            elif self.current_char == '^':
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TT_LSQUAREBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TT_RSQUAREBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char == '?':
                tokens.append(Token(TT_QUESTIONMARK, pos_start=self.pos))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharacterError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        if self.debug:
            print(tokens)
        return tokens, None

    def make_number(self):
        number_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            number_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(number_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(number_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        token_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(token_type, id_str, pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NOTEQUALS, pos_start=pos_start), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "(after '!')", '=')

    def make_equals(self):
        token_type = TT_EQUALS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_DOUBLEEQUALS

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        token_type = TT_LESS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_LESSEQUALS

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        token_type = TT_GREATER
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_GREATEREQUALS

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_minus_or_arrow(self):
        token_type = TT_MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '>':
            self.advance()
            token_type = TT_ARROW

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_string(self, chartype):
        string = ''
        chartype = chartype
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t',
            '\\': '\\',
            '"': '"',
            '\'': '\''
        }

        while self.current_char != chartype and self.current_char is not None or escape_character:
            if escape_character:
                try:
                    string += escape_characters[self.current_char]
                    escape_character = False
                except KeyError:
                    return None, InvalidSyntaxError(pos_start, self.pos, "Invalid escape character type: '" + self.current_char + "'")
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()

        if self.current_char == None:
            return None, InvalidSyntaxError(pos_start, self.pos, "Unterminated string")

        self.advance()
        return Token(TT_STRING, string, pos_start, self.pos), None

    def make_comment_or_div(self):
        pos_start = self.pos.copy()
        token_type = TT_DIV
        self.advance()

        if self.current_char == '/':
            while self.current_char is not None and self.current_char not in '\n;':
                self.advance()
            return None

        return Token(TT_DIV, pos_start=pos_start, pos_end=self.pos)

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_POW = 'POW'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_KEYWORD = 'KEYWORD'
TT_IDENTIFIER = 'IDENTIFIER'
TT_EQUALS = 'EQUALS'
TT_DOUBLEEQUALS = 'DOUBLEEQUALS'
TT_NOTEQUALS = 'NOTEQUALS'
TT_LESS = 'LESS'
TT_LESSEQUALS = 'LESSEQUALS'
TT_GREATER = 'GREATER'
TT_GREATEREQUALS = 'GREATEREQUALS'
TT_COMMA = 'COMMA'
TT_ARROW = 'ARROW'
TT_STRING = 'STRING'
TT_LSQUAREBRACKET = 'LSQUAREBRACKET'
TT_RSQUAREBRACKET = 'RSQUAREBRACKET'
TT_QUESTIONMARK = 'QUESTIONMARK'
TT_NEWLINE = 'NEWLINE'
TT_EOF = 'EOF'

KEYWORDS = [
    'set',
    'and',
    'or',
    'not',
    'if',
    'then',
    'elif',
    'else',
    'for',
    'to',
    'step',
    'while',
    'func',
    'end',
    'return',
    'continue',
    'break'
]

ERROR_KEYWORDS = [
    "set",
    "if",
    "func",
    "while",
    "for",
    "log",
    "str_input",
    "num_input",
    "is_digit",
    "random_int",
    "clear",
    "is_number",
    "is_string",
    "is_list",
    "is_function",
    "append",
    "pop",
    "len",
    "extend",
]


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def __repr__(self):
        if self.value or self.value == 0:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

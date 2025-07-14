from rply import LexerGenerator


class Lexer:
    def __init__(self):
        self.lg = LexerGenerator()

    def _add_tokens(self):
        self.lg.ignore(r'/\*[\s\S]*?\*/')
        self.lg.ignore(r'//[^\n]*')


        # Data types
        self.lg.add('FLOAT', r'\d+\.\d+')
        self.lg.add('INTEGER', r'\d+')
        self.lg.add('STRING', r'\"[^\"]*\"')

        # Type keywords
        self.lg.add('NUMBER_TYPE', r'number')
        self.lg.add('BOOL_TYPE', r'bool')
        self.lg.add('VEC3_TYPE', r'vec3')

        # Boolean literals
        self.lg.add('TRUE', r'true')
        self.lg.add('FALSE', r'false')

        # Vector operations
        self.lg.add('VEC_X', r'\.x')
        self.lg.add('VEC_Y', r'\.y')
        self.lg.add('VEC_Z', r'\.z')

        self.lg.add('DOT', r'\*')
        self.lg.add('CROSS', r'\^')

        # Keywords
        self.lg.add('PRINT', r'print')
        self.lg.add('IF', r'if')

        # Operators
        self.lg.add('PLUS', r'\+')
        self.lg.add('MINUS', r'-')
        self.lg.add('MULTIPLY', r'\*')
        self.lg.add('DIVIDE', r'/')
        self.lg.add('ASSIGN', r'=')

        # Comparison operators
        self.lg.add('EQ', r'==')
        self.lg.add('LE', r'<=')
        self.lg.add('GE', r'>=')
        self.lg.add('LT', r'<')
        self.lg.add('GT', r'>')

        # Logical operators
        self.lg.add('AND', r'and')
        self.lg.add('OR', r'or')
        self.lg.add('NOT', r'not')
        self.lg.add('XOR', r'xor')
        self.lg.add('NOR', r'nor')
        self.lg.add('NAND', r'nand')
        self.lg.add('XNOR', r'xnor')

        # Delimiters
        self.lg.add('LPAREN', r'\(')
        self.lg.add('RPAREN', r'\)')
        self.lg.add('LBRACE', r'\{')
        self.lg.add('RBRACE', r'\}')
        self.lg.add('COLON', r'\:')
        self.lg.add('COMMA', r'\,')

        # Colors
        self.lg.add('COLOR_TYPE', 'COLOR.')

        self.lg.add('RESERVED_IDENTIFIER', r'\$[a-zA-Z_][a-zA-Z0-9_]*')
        self.lg.add('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*')

        # Ignore whitespace
        self.lg.ignore(r'\s+')

    def build(self):
        self._add_tokens()
        return self.lg.build()

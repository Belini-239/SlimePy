import warnings

from rply import ParserGenerator, Token
from generator.ast_nodes import *

from error_handler import ErrorHandler


class Parser:
    def __init__(self):
        # Define all tokens explicitly
        tokens = [
            'IDENTIFIER', 'RESERVED_IDENTIFIER',
            # Data types
            'INTEGER', 'FLOAT', 'STRING',
            # Type keywords
            'NUMBER_TYPE', 'BOOL_TYPE', 'VEC3_TYPE',
            'COLOR_TYPE',
            # Boolean literals
            'TRUE', 'FALSE',
            # Vector operations
            'DOT', 'CROSS',
            'VEC_X', 'VEC_Y', 'VEC_Z',
            # Keywords
            'PRINT', 'IF', 'ELSE',
            # Operators
            'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'ASSIGN',
            # Comparison operators
            'EQ', 'LT', 'GT', 'LE', 'GE',
            # Logical operators
            'AND', 'OR', 'NOT', 'XOR', 'XNOR', 'NAND', 'NOR',
            # Delimiters
            'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
            'COLON', 'COMMA',
            # Globals
            'GLOBAL',
        ]

        warnings.filterwarnings("ignore")

        self.pg = ParserGenerator(
            tokens,
            precedence=[
                ('left', ['AND', 'OR', 'XOR', 'XNOR', 'NAND', 'NOR']),
                ('nonassoc', ['LT', 'LE', 'GT', 'GE', 'EQ']),
                ('left', ['PLUS', 'MINUS']),
                ('left', ['MULTIPLY', 'DIVIDE']),
                ('left', ['DOT', 'CROSS']),
                ('right', ['NOT', 'UMINUS']),
                ('left', ['VEC_X', 'VEC_Y', 'VEC_Z'])
            ]

        )

    def parse(self):
        @self.pg.production('program : global_statement_list block')
        def program(p):
            return [p[0], p[1]]

        @self.pg.production('block : LBRACE statement_list RBRACE')
        def block_braces(p):
            return Block(p[1], p[0])

        @self.pg.production('statement_list : ')
        @self.pg.production('statement_list : statement')
        @self.pg.production('statement_list : statement statement_list')
        def statement_list(p):
            if len(p) == 0:
                return []
            if len(p) == 1:
                return [p[0]]
            return [p[0]] + p[1]

        @self.pg.production('global_statement_list : ')
        @self.pg.production('global_statement_list : global_statement')
        @self.pg.production('global_statement_list : global_statement global_statement_list')
        def global_statement_list(p):
            if len(p) == 0:
                return []
            if len(p) == 1:
                return [p[0]]
            return [p[0]] + p[1]

        @self.pg.production('global_statement : global_declaration')
        def global_statement(p):
            return p[0]

        @self.pg.production('global_declaration : global_declaration_start COLON type')
        def global_declaration_start(p):
            for name in p[0]:
                ErrorHandler.variables.add(name)
            return GlobalDeclaration(p[0], p[2], p[1])

        @self.pg.production('global_declaration_start : global_declaration_start COMMA IDENTIFIER')
        def global_declaration_start(p):
            return p[0] + [p[2].value]

        @self.pg.production('global_declaration_start : GLOBAL IDENTIFIER')
        def global_declaration_start(p):
            return [p[1].value]

        @self.pg.production('statement : declaration')
        @self.pg.production('statement : assignment')
        @self.pg.production('statement : print_statement')
        @self.pg.production('statement : if_statement')
        @self.pg.production('statement : block')
        @self.pg.production('statement : function_call')
        def statement(p):
            return p[0]

        @self.pg.production('primary : function_call')
        def primary_function(p):
            return p[0]

        @self.pg.production('function_call : IDENTIFIER LPAREN argument_list RPAREN')
        def function_call(p):
            return FunctionCall(p[0].value, p[2], p[0])

        @self.pg.production('argument_list : ')
        def empty_arguments(p):
            return []

        @self.pg.production('argument_list : expression')
        def single_argument(p):
            return [p[0]]

        @self.pg.production('argument_list : expression COMMA argument_list')
        def multiple_arguments(p):
            return [p[0]] + p[2]

        @self.pg.production('declaration : IDENTIFIER COLON type ASSIGN expression')
        def declaration(p):
            var_type = p[2]
            var_name = p[0].value

            ErrorHandler.variables.add(var_name)

            return Declaration(var_name, var_type, p[4], p[0])

        @self.pg.production('type : NUMBER_TYPE')
        @self.pg.production('type : BOOL_TYPE')
        @self.pg.production('type : VEC3_TYPE')
        def type_spec(p):
            res_type = ''
            if p[0].gettokentype() == 'NUMBER_TYPE':
                res_type = 'number'
            if p[0].gettokentype() == 'BOOL_TYPE':
                res_type = 'bool'
            if p[0].gettokentype() == 'VEC3_TYPE':
                res_type = 'vec3'
            return res_type

        @self.pg.production('assignment : IDENTIFIER ASSIGN expression')
        @self.pg.production('assignment : RESERVED_IDENTIFIER ASSIGN expression')
        def assignment(p):
            return Assignment(p[0].value, p[2], p[0])

        @self.pg.production('print_statement : PRINT LPAREN expression RPAREN')
        def print_statement(p):
            return Print(p[2], p[0])

        @self.pg.production('if_statement : IF LPAREN expression RPAREN block')
        @self.pg.production('if_statement : IF LPAREN expression RPAREN block ELSE block')
        def if_statement(p):
            false_block = p[6] if len(p) > 5 else None
            return If(p[2], p[4], p[0], false_block)

        @self.pg.production('expression : expression VEC_X')
        @self.pg.production('expression : expression VEC_Y')
        @self.pg.production('expression : expression VEC_Z')
        def vector_component(p):
            component = p[1].gettokentype().replace('VEC_', '').lower()
            return VectorComponent(p[0], component, p[1])

        @self.pg.production('expression : NOT expression')
        def not_expression(p):
            return UnaryOp('not', p[1], p[0])

        @self.pg.production('expression : MINUS expression', precedence='UMINUS')
        def unary_minus(p):
            return UnaryOp('-', p[1], p[0])

        @self.pg.production('expression : expression DOT expression')
        @self.pg.production('expression : expression CROSS expression')
        @self.pg.production('expression : expression PLUS expression')
        @self.pg.production('expression : expression MINUS expression')
        @self.pg.production('expression : expression MULTIPLY expression')
        @self.pg.production('expression : expression DIVIDE expression')
        @self.pg.production('expression : expression EQ expression')
        @self.pg.production('expression : expression LT expression')
        @self.pg.production('expression : expression GT expression')
        @self.pg.production('expression : expression LE expression')
        @self.pg.production('expression : expression GE expression')
        @self.pg.production('expression : expression AND expression')
        @self.pg.production('expression : expression OR expression')
        @self.pg.production('expression : expression XOR expression')
        @self.pg.production('expression : expression NOR expression')
        @self.pg.production('expression : expression XNOR expression')
        @self.pg.production('expression : expression NAND expression')
        def comparison_expression(p):
            return BinaryOp(p[0], p[1].value, p[2], p[1])

        @self.pg.production('expression : term')
        def expression_term(p):
            return p[0]

        @self.pg.production('term : factor')
        def term_factor(p):
            return p[0]

        @self.pg.production('factor : primary')
        def factor_primary(p):
            return p[0]

        @self.pg.production('primary : INTEGER')
        def primary_integer(p):
            return Number(int(p[0].value), p[0])

        @self.pg.production('primary : FLOAT')
        def primary_float(p):
            return Number(float(p[0].value), p[0])

        @self.pg.production('primary : STRING')
        def primary_string(p):
            return StringLiteral(p[0].value[1:-1], p[0])

        @self.pg.production('primary : TRUE')
        def primary_true(p):
            return Boolean(True, p[0])

        @self.pg.production('primary : FALSE')
        def primary_false(p):
            return Boolean(False, p[0])

        @self.pg.production('primary : COLOR_TYPE IDENTIFIER')
        def primary_color(p):
            color = p[1].value.title()
            return Color(color, p[1])

        @self.pg.production('primary : RESERVED_IDENTIFIER')
        def primary_identifier(p):
            return ReservedIdentifier(p[0].value, p[0])

        @self.pg.production('primary : IDENTIFIER')
        def primary_identifier(p):
            return Identifier(p[0].value, p[0])

        @self.pg.production('primary : vec3_constructor')
        def primary_vec3(p):
            return p[0]

        @self.pg.production('vec3_constructor : VEC3_TYPE LPAREN expression COMMA expression COMMA expression RPAREN')
        def vec3_constructor(p):
            return Vec3(p[2], p[4], p[6], p[0])

        @self.pg.production('primary : LPAREN expression RPAREN')
        def primary_parens(p):
            return p[1]

        @self.pg.error
        def error_handler(token):
            ErrorHandler.error(f"Unexpected token {token}", token)

    def build(self):
        self.parse()
        return self.pg.build()


# Enhanced AST Printer with Type Information
def print_ast(node, indent=0):
    """Recursively prints AST structure with type information"""
    indent_str = "  " * indent

    if isinstance(node, Block):
        print(f"{indent_str}Block [type: {node.type}]")
        for i, stmt in enumerate(node.statements):
            print(f"{indent_str}  Statement {i + 1}:")
            print_ast(stmt, indent + 2)
        print(f"{indent_str}]")

    elif isinstance(node, Declaration):
        print(f"{indent_str}Declaration [type: {node.type}]")
        print(f"{indent_str}  Name: {node.name}")
        print(f"{indent_str}  Var Type: {node.var_type}")
        print(f"{indent_str}  Expression:")
        print_ast(node.expr, indent + 2)

    elif isinstance(node, Assignment):
        print(f"{indent_str}Assignment [type: {node.type}]")
        print(f"{indent_str}  Name: {node.name}")
        print(f"{indent_str}  Expression:")
        print_ast(node.expr, indent + 2)

    elif isinstance(node, Print):
        print(f"{indent_str}Print [type: {node.type}]")
        print(f"{indent_str}  Expression:")
        print_ast(node.expr, indent + 1)

    elif isinstance(node, If):
        print(f"{indent_str}If [type: {node.type}]")
        print(f"{indent_str}  Condition [type: {node.condition.type}]:")
        print_ast(node.condition, indent + 2)
        print(f"{indent_str}  True Block:")
        print_ast(node.true_block, indent + 2)
        if node.false_block:
            print(f"{indent_str}  False Block:")
            print_ast(node.false_block, indent + 2)

    elif isinstance(node, BinaryOp):
        print(f"{indent_str}BinaryOp [type: {node.type}, op: {node.op}]")
        print(f"{indent_str}  Left [type: {node.left.type if hasattr(node.left, 'type') else 'N/A'}]:")
        print_ast(node.left, indent + 2)
        print(f"{indent_str}  Right [type: {node.right.type if hasattr(node.right, 'type') else 'N/A'}]:")
        print_ast(node.right, indent + 2)

    elif isinstance(node, UnaryOp):
        print(f"{indent_str}UnaryOp [type: {node.type}, op: {node.op}]")
        print(f"{indent_str}  Expression [type: {node.expr.type if hasattr(node.expr, 'type') else 'N/A'}]:")
        print_ast(node.expr, indent + 2)

    elif isinstance(node, Vec3):
        print(f"{indent_str}Vec3 [type: {node.type}]")
        print(f"{indent_str}  X: {node.x}")
        print(f"{indent_str}  Y: {node.y}")
        print(f"{indent_str}  Z: {node.z}")

    elif isinstance(node, VectorComponent):
        print(f"{indent_str}VectorComponent [type: {node.type}]")
        print(f"{indent_str}  Vector:")
        print_ast(node.vector, indent + 2)
        print(f"{indent_str}  Component: {node.component}")

    elif isinstance(node, FunctionCall):
        print(f"{indent_str}FunctionCall [name: {node.name}]")
        print(f"{indent_str}  Arguments:")
        for i, arg in enumerate(node.args):
            print(f"{indent_str}    Arg {i + 1}:")
            print_ast(arg, indent + 4)

    elif isinstance(node, Color):
        print(f"{indent_str}Color({node.color})")

    elif isinstance(node, (Number, Boolean, StringLiteral, Identifier, ReservedIdentifier)):
        type_info = f" [type: {node.type}]" if hasattr(node, 'type') else ""
        print(f"{indent_str}{node.__class__.__name__}{type_info}: {node}")

    else:
        print(f"{indent_str}Unknown node: {type(node)}")

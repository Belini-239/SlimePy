import sys

from generator.lexer import Lexer
from generator.parser import Parser
from construct import Constructor
from error_handler import ErrorHandler


def check_code():
    path_in = sys.argv[1]

    with open(path_in) as file:
        code = file.read()

    ErrorHandler.is_building = False

    lexer = Lexer().build()
    tokens = list(lexer.lex(code))
    parser = Parser().build()

    ast = parser.parse(iter(tokens))
    constructor = Constructor()
    constructor.full_construct(ast[1], ast[0])

    ErrorHandler.no_error()


def build_code():
    path_in = sys.argv[1]
    path_out = sys.argv[2]

    with open(path_in) as file:
        code = file.read()

    ErrorHandler.is_building = True

    lexer = Lexer().build()
    tokens = list(lexer.lex(code))

    parser = Parser().build()
    ast = parser.parse(iter(tokens))
    constructor = Constructor()
    constructor.full_construct(ast[1], ast[0])

    constructor.graph.optimize()

    with open(path_out, "w") as file:
        file.write(constructor.graph.get_text())


if __name__ == "__main__":

    if len(sys.argv) == 2:
        check_code()
    else:
        build_code()

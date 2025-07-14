import sys

from generator.lexer import Lexer
from generator.parser import Parser
from construct import Constructor

if __name__ == "__main__":
    path_in = sys.argv[1]
    path_out = sys.argv[2]

    with open(path_in) as file:
        code = file.read()

    lexer = Lexer().build()
    tokens = list(lexer.lex(code))

    parser = Parser().build()
    ast = parser.parse(iter(tokens))

    constructor = Constructor()
    constructor.full_construct(ast)

    with open(path_out, "w") as file:
        file.write(constructor.graph.get_text())

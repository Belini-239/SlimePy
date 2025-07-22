import json

from rply import Token
from generator.variables import VarsManager


class ErrorHandler:
    is_building = False
    variables = set()
    functions = set()

    @classmethod
    def set_building(cls, is_building):
        cls.is_building = is_building

    @classmethod
    def error(cls, message, token: Token):
        if cls.is_building:
            raise Exception(f'{message} on position: line {token.source_pos.lineno} col {token.source_pos.colno}')
        else:
            output = {
                "variables": list(cls.variables),
                "functions": list(cls.functions),
                "errors": [
                    {
                        "range": {
                            "start": {"line": token.source_pos.lineno - 1, "character": token.source_pos.colno - 1},
                            "end": {"line": token.source_pos.lineno - 1,
                                    "character": token.source_pos.colno + len(token.value) - 2}
                        },
                        "message": message,
                        "severity": 1
                    }
                ]}
            print(json.dumps(output))
            exit(0)

    @classmethod
    def no_error(cls):
        output = {
            "variables": list(cls.variables),
            "functions": list(cls.functions),
            "errors": []
        }
        print(json.dumps(output))
        exit(0)

from builder.graph import Graph
from generator.ast_nodes import *


class BuiltInFunction:
    def __init__(self, name: str, args: list, return_type: str, func):
        self.name = name
        self.args = args
        self.return_type = return_type
        self.func = func


class BuiltInRegister:
    _registry = {}
    _graph = None

    @classmethod
    def set_graph(cls, graph: Graph):
        cls._graph = graph

    @classmethod
    def register(cls, name: str, args: list, return_type: str):
        def decorator(func):
            cls._registry[name] = BuiltInFunction(name, args, return_type, func)
            return func
        return decorator

    @classmethod
    def call(cls, name: str, args: list, node):
        if name not in cls._registry:
            raise Exception(f'No such function: {name}')
        func = cls._registry[name]
        if len(args) != len(func.args):
            raise Exception(f'Wrong number of arguments: {name} needs {len(func.args)}')

        flag = True
        for i in range(len(args)):
            if func.args[i] == 'c_number':
                if isinstance(args[i], Number):
                    continue
                else:
                    flag = False
            if args[i].type != func.args[i]:
                flag = False
        if not flag:
            raise Exception(f'Wrong types of arguments: {name} needs {str(func.args)}')
        node.type = func.return_type
        func.func(cls._graph, node, *args)

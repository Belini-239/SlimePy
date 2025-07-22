from builder.graph import Graph
from generator.ast_nodes import *
from types_table import TypesTable


class Function:
    def __init__(self, name: str, args: list, return_type: str, func=None, block=None, args_names=None):
        self.name = name
        self.args = args
        self.return_type = return_type
        self.args_names = args_names
        self.func = func
        self.block = block


class BuiltInRegister:
    _registry = {}
    _registry_custom = {}
    _graph = None

    @classmethod
    def set_graph(cls, graph: Graph):
        cls._graph = graph

    @classmethod
    def register(cls, name: str, args: list, return_type: str):
        def decorator(func):
            cls._registry[name] = Function(name, args, return_type, func=func)
            return func

        return decorator

    @classmethod
    def register_custom(cls, var_name: str, args: list, return_type: str, block):
        args_t = []
        args_n = []
        for name, var_type in args:
            args_t.append(var_type)
            args_n.append(name)
        cls._registry_custom[var_name] = Function(var_name, args_t, return_type, block=block, args_names=args_n)

    @classmethod
    def check_builtin_function(cls, name: str):
        return name in cls._registry

    @classmethod
    def check_function(cls, name: str):
        return name in cls._registry_custom

    @classmethod
    def check_types(cls, func_args: list, call_args: list):
        flag = True
        for i in range(len(func_args)):
            if func_args[i] == 'c_number':
                if isinstance(call_args[i], Number):
                    continue
                else:
                    flag = False
            if call_args[i].type != func_args[i]:
                if TypesTable.check(call_args[i].type, func_args[i]):
                    TypesTable.transform(cls._graph, call_args[i].type, func_args[i], call_args[i])
                else:
                    flag = False
        return flag

    @classmethod
    def get_function(cls, name: str, args: list) -> Function:
        if name not in cls._registry_custom:
            raise Exception(f'No such function: {name}')
        func = cls._registry_custom[name]
        if len(args) != len(func.args):
            raise Exception(f'Wrong number of arguments: {name} needs {len(func.args)}')
        if not BuiltInRegister.check_types(func.args, args):
            raise Exception(f'Wrong types of arguments: {name} needs {str(func.args)}')
        return func

    @classmethod
    def call(cls, name: str, args: list, node):
        if name not in cls._registry:
            raise Exception(f'No such function: {name}')
        func = cls._registry[name]
        if len(args) != len(func.args):
            raise Exception(f'Wrong number of arguments: {name} needs {len(func.args)}')
        if not BuiltInRegister.check_types(func.args, args):
            raise Exception(f'Wrong types of arguments: {name} needs {str(func.args)}')
        node.type = func.return_type
        func.func(cls._graph, node, *args)

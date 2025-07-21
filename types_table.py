import builder.nodes.nodes as ns
from generator.ast_nodes import *
from optimizer import Optimizer
from builder.graph import Graph


class TypesTable:
    _table = {}

    @classmethod
    def register(cls, type_from: str, type_to: str):
        def decorator(func):
            cls._table[f'{type_from} => {type_to}'] = func
            return func

        return decorator

    @classmethod
    def check(cls, type_from: str, type_to: str):
        return f'{type_from} => {type_to}' in cls._table

    @classmethod
    def transform(cls, graph: Graph, type_from: str, type_to: str, node: Node):
        if not TypesTable.check(type_from, type_to):
            return
        cls._table[f'{type_from} => {type_to}'](graph, node)


@TypesTable.register('str', 'country')
def str_country(graph: Graph, node: StringLiteral):
    tmp = Optimizer.add_node(graph, ns.CountryNode(node.value), {})
    node.SID = tmp.ports['out']


@TypesTable.register('str', 'color')
def str_country(graph: Graph, node: StringLiteral):
    tmp = Optimizer.add_node(graph, ns.ColorNode(node.value), {})
    node.SID = tmp.ports['out']

from builder.graph import Graph
from builder.node import Node


class Optimizer:
    _optimize_dict = {}

    @classmethod
    def add_node(cls, graph: Graph, node: Node, inputs: dict) -> Node:
        res_hash = node.node_hash + ':'
        for port in sorted(inputs.keys()):
            res_hash += str(inputs[port]) + ','
        if res_hash not in cls._optimize_dict:
            graph.add_node(node)
            for port, SID in inputs.items():
                graph.add_edge(SID, node.ports[port])
            cls._optimize_dict[res_hash] = node
        return cls._optimize_dict[res_hash]

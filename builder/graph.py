import json
import os

from builder.node import Node, gen_id


class Graph:

    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, port_from, port_to):
        self.edges.append((port_from, port_to))

    def get_text(self) -> str:
        result = "{\"serializableNodes\": ["
        result += ",".join([node.node_text for node in self.nodes])
        result += "],\"serializableConnections\": ["
        path = os.path.dirname(os.path.abspath(__file__)) + "/nodes_json/"
        with open(path + "connection.json") as f:
            base_connection = f.read()
        for port_from, port_to in self.edges:
            connection_txt = base_connection[:]
            connection_txt = connection_txt.replace("{sID}", gen_id())
            connection_txt = connection_txt.replace("{fromID}", port_from)
            connection_txt = connection_txt.replace("{toID}", port_to)
            result = result + connection_txt + ","
        if len(self.edges) > 0:
            result = result[:-1]
        result = result + "]}"
        json_obj = json.loads(result)
        result = json.dumps(json_obj, separators=(',', ':'))
        return result

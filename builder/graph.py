import json
import os

from builder.node import Node, gen_id


class Graph:

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.ports = {}
        self.back_edges = {}

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, port_from, port_to):
        if port_to is None or port_from is None:
            return
        self.edges.append((port_from, port_to))

    def optimize(self):
        used = {}
        start_points = []
        for node in self.nodes:
            used[node.id] = False
            if node.is_terminated:
                start_points.append(node.id)
            for port in node.ports.values():
                self.ports[port] = node.id
            self.back_edges[node.id] = []

        for port_from, port_to in self.edges:
            self.back_edges[self.ports[port_to]].append(self.ports[port_from])

        for node_id in start_points:
            self.run_dfs(node_id, used)

        nodes = []
        edges = []

        for node in self.nodes:
            if used[node.id]:
                nodes.append(node)
            else:
                print(node.node_hash, 'cutted off')

        for port_from, port_to in self.edges:
            if used[self.ports[port_from]] and used[self.ports[port_to]]:
                edges.append((port_from, port_to))

        self.nodes = nodes
        self.edges = edges

    def run_dfs(self, node_id, used):
        if used[node_id]:
            return
        used[node_id] = True
        for next_id in self.back_edges[node_id]:
            self.run_dfs(next_id, used)

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

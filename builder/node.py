import os
import uuid
import json


def gen_id() -> str:
    return str(uuid.uuid4())


class Node:
    def __init__(self, node_file, ports: list = None, args: dict = None):
        self.node_hash = type(self).__name__ + str(args)
        if args is None:
            args = {}
        if ports is None:
            ports = []

        self.args = args

        self.ports = {}
        for port in ports:
            self.ports[port] = gen_id()

        self.id = gen_id()

        path = os.path.dirname(os.path.abspath(__file__)) + "/nodes_json/"
        with open(path + node_file, 'r') as f:
            node_text = f.read()
        for port_name, port_id in self.ports.items():
            node_text = node_text.replace("{" + port_name + "}", self.ports[port_name])

        for key, value in args.items():
            node_text = node_text.replace("{" + key + "}", str(value))

        node_text = node_text.replace("{sID}", self.id)
        self.node_text = node_text

        self.is_terminated = False


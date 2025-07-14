from generator.functions import *
from builder.graph import Graph
import builder.nodes.nodes as ns


# ======= FLOAT =======

# clamp(value: number, min: number, max: number) -> number
@BuiltInRegister.register('clamp', ['number', 'number', 'number'], 'number')
def builtin_clamp(graph: Graph, node, value, minv, maxv):
    tmp = ns.ClampFloatNode()
    node.SID = tmp.ports['out']
    graph.add_node(tmp)

    graph.add_edge(value.SID, tmp.ports['value'])
    graph.add_edge(minv.SID, tmp.ports['min'])
    graph.add_edge(maxv.SID, tmp.ports['max'])


@BuiltInRegister.register('abs', ['number'], 'number')
@BuiltInRegister.register('round', ['number'], 'number')
@BuiltInRegister.register('floor', ['number'], 'number')
@BuiltInRegister.register('ceil', ['number'], 'number')
@BuiltInRegister.register('sin', ['number'], 'number')
@BuiltInRegister.register('cos', ['number'], 'number')
@BuiltInRegister.register('tan', ['number'], 'number')
@BuiltInRegister.register('asin', ['number'], 'number')
@BuiltInRegister.register('acos', ['number'], 'number')
@BuiltInRegister.register('atan', ['number'], 'number')
@BuiltInRegister.register('sqrt', ['number'], 'number')
@BuiltInRegister.register('sign', ['number'], 'number')
@BuiltInRegister.register('log', ['number'], 'number')
@BuiltInRegister.register('log10', ['number'], 'number')
@BuiltInRegister.register('pow_e', ['number'], 'number')
@BuiltInRegister.register('pow_10', ['number'], 'number')
def builtin_operations(graph: Graph, node, x):
    tmp = ns.OperationNode(node.name)
    node.SID = tmp.ports['out']
    graph.add_node(tmp)

    graph.add_edge(x.SID, tmp.ports['in'])


# random(min: number, max: number) -> number
@BuiltInRegister.register('random', ['number', 'number'], 'number')
def builtin_random(graph: Graph, node, minv, maxv):
    tmp = ns.RandomFloatNode()
    node.SID = tmp.ports['out']
    graph.add_node(tmp)
    graph.add_edge(minv.SID, tmp.ports['min'])
    graph.add_edge(maxv.SID, tmp.ports['max'])


# ======= VECTOR =======

# distance(start: vec3, end: vec3) -> number
@BuiltInRegister.register('distance', ['vec3', 'vec3'], 'number')
def builtin_distance(graph: Graph, node, start, end):
    tmp = ns.DistanceNode()
    node.SID = tmp.ports['out']
    graph.add_node(tmp)

    graph.add_edge(start.SID, tmp.ports['in1'])
    graph.add_edge(end.SID, tmp.ports['in2'])


# len(vector: vec3) -> number
@BuiltInRegister.register('len', ['vec3'], 'number')
def builtin_len(graph: Graph, node, vector):
    tmp = ns.MagnitudeNode()
    node.SID = tmp.ports['out']
    graph.add_node(tmp)

    graph.add_edge(vector.SID, tmp.ports['in'])


# norm(vector: vec3) -> vec3
@BuiltInRegister.register('norm', ['vec3'], 'vec3')
def builtin_normalize(graph: Graph, node, vector):
    tmp = ns.NormalizeNode()
    node.SID = tmp.ports['out']
    graph.add_node(tmp)

    graph.add_edge(vector.SID, tmp.ports['in'])


# ======= DEBUG =======

# draw_line(start: vec3, end: vec3, thickness: number, c: color) -> none
@BuiltInRegister.register('draw_line', ['vec3', 'vec3', 'number', 'color'], 'none')
def builtin_draw_line(graph: Graph, node, start, end, thickness, color):
    tmp = ns.DrawLineNode()
    graph.add_node(tmp)

    graph.add_edge(start.SID, tmp.ports['start'])
    graph.add_edge(end.SID, tmp.ports['end'])
    graph.add_edge(thickness.SID, tmp.ports['thick'])
    graph.add_edge(color.SID, tmp.ports['color'])


# draw_disc(pos: vec3, radius: number, thickness: number, c: color) -> none
@BuiltInRegister.register('draw_disc', ['vec3', 'number', 'number', 'color'], 'none')
def builtin_draw_line(graph: Graph, node, pos, radius, thickness, color):
    tmp = ns.DrawDiscNode()
    graph.add_node(tmp)

    graph.add_edge(pos.SID, tmp.ports['pos'])
    graph.add_edge(radius.SID, tmp.ports['radius'])
    graph.add_edge(thickness.SID, tmp.ports['thick'])
    graph.add_edge(color.SID, tmp.ports['color'])

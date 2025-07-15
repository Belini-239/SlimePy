from generator.functions import *
from builder.graph import Graph
import builder.nodes.nodes as ns
from optimizer import Optimizer


# ======= FLOAT =======

# clamp(value: number, min: number, max: number) -> number
@BuiltInRegister.register('clamp', ['number', 'number', 'number'], 'number')
def builtin_clamp(graph: Graph, node, value, minv, maxv):
    tmp = Optimizer.add_node(graph, ns.ClampFloatNode(), {'value': value.SID, 'min': minv.SID, 'max': maxv.SID})
    node.SID = tmp.ports['out']


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
    tmp = Optimizer.add_node(graph, ns.OperationNode(node.name), {'in': x.SID})
    node.SID = tmp.ports['out']


# random(min: number, max: number) -> number
@BuiltInRegister.register('random', ['number', 'number'], 'number')
def builtin_random(graph: Graph, node, minv, maxv):
    tmp = Optimizer.add_node(graph, ns.RandomFloatNode(), {'min': minv.SID, 'max': maxv.SID})
    node.SID = tmp.ports['out']


# ======= VECTOR =======

# distance(start: vec3, end: vec3) -> number
@BuiltInRegister.register('distance', ['vec3', 'vec3'], 'number')
def builtin_distance(graph: Graph, node, start, end):
    tmp = Optimizer.add_node(graph, ns.DistanceNode(), {'in1': start.SID, 'in2': end.SID})
    node.SID = tmp.ports['out']


# len(vector: vec3) -> number
@BuiltInRegister.register('len', ['vec3'], 'number')
def builtin_len(graph: Graph, node, vector):
    tmp = Optimizer.add_node(graph, ns.MagnitudeNode(), {'in': vector.SID})
    node.SID = tmp.ports['out']


# norm(vector: vec3) -> vec3
@BuiltInRegister.register('norm', ['vec3'], 'vec3')
def builtin_normalize(graph: Graph, node, vector):
    tmp = Optimizer.add_node(graph, ns.NormalizeNode(), {'in': vector.SID})
    node.SID = tmp.ports['out']


# ======= DEBUG =======

# draw_line(start: vec3, end: vec3, thickness: number, c: color) -> none
@BuiltInRegister.register('draw_line', ['vec3', 'vec3', 'number', 'color'], 'none')
def builtin_draw_line(graph: Graph, node, start, end, thickness, color):
    tmp = Optimizer.add_node(graph, ns.DrawLineNode(), {'start': start.SID, 'end': end.SID, 'thick': thickness.SID,
                                                        'color': color.SID})


# draw_disc(pos: vec3, radius: number, thickness: number, c: color) -> none
@BuiltInRegister.register('draw_disc', ['vec3', 'number', 'number', 'color'], 'none')
def builtin_draw_line(graph: Graph, node, pos, radius, thickness, color):
    tmp = Optimizer.add_node(graph, ns.DrawDiscNode(), {'pos': pos.SID, 'radius': radius.SID, 'thick': thickness.SID,
                                                        'color': color.SID})

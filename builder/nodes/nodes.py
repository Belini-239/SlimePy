import random

from builder.node import Node


# =========== FLOAT ==========
class FloatNode(Node):
    def __init__(self, value: float):
        super().__init__('float.json', ['out'], {'value': value})


class AddFloatsNode(Node):
    def __init__(self):
        super().__init__('add_floats.json', ['in1', 'in2', 'out'])


class DivideFloatsNode(Node):
    def __init__(self):
        super().__init__('divide_floats.json', ['in1', 'in2', 'out'])


class SubtractFloatsNode(Node):
    def __init__(self):
        super().__init__('subtract_floats.json', ['in1', 'in2', 'out'])


class MultiplyFloatsNode(Node):
    def __init__(self):
        super().__init__('multiply_floats.json', ['in1', 'in2', 'out'])


class ClampFloatNode(Node):
    def __init__(self):
        super().__init__('clamp_float.json', ['value', 'min', 'max', 'out'])


class ConditionalFloatNode(Node):
    def __init__(self):
        super().__init__('conditional_set_float.json', ['in1', 'in2', 'cond', 'out'])


class OperationNode(Node):
    def __init__(self, operator):
        ops = ['abs', 'round', 'floor', 'ceil', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sqrt', 'sign',
               'ln', 'log10', 'pow_e', 'pow_10']
        op = ops.index(operator)
        super().__init__('operation.json', ['in', 'out'], {'operation': op})


class RandomFloatNode(Node):
    def __init__(self):
        super().__init__('random_float.json', ['min', 'max', 'out'])
        self.node_hash = f"RandomFloatNode{random.random()}"


class CompareFloatsNode(Node):
    def __init__(self, operator):
        ops = ['==', '<', '>', '<=', '>=']
        op = ops.index(operator)
        super().__init__('compare_floats.json', ['in1', 'in2', 'out'], {'operation': op})


# =========== BOOL ==========
class BoolNode(Node):
    def __init__(self, value: bool):
        super().__init__('bool.json', ['out'], {'value': 0 if value else 1})


class CompareBoolsNode(Node):
    def __init__(self, operator):
        ops = ['and', 'or', 'eq', 'xor', 'nor', 'nand', 'xnor']
        op = ops.index(operator)
        super().__init__('compare_bools.json', ['in1', 'in2', 'out'], {'operator': op})


class NotNode(Node):
    def __init__(self):
        super().__init__('not.json', ['in', 'out'])


# =========== VECTOR ==========
class VectorNode(Node):
    def __init__(self):
        super().__init__('construct_vector.json', ['x', 'y', 'z', 'out'])


class SplitVectorNode(Node):
    def __init__(self):
        super().__init__('split_vector.json', ['x', 'y', 'z', 'in'])


class CrossProductNode(Node):
    def __init__(self):
        super().__init__('cross_product.json', ['in1', 'in2', 'out'])


class DotProductNode(Node):
    def __init__(self):
        super().__init__('dot_product.json', ['in1', 'in2', 'out'])


class AddVectorsNode(Node):
    def __init__(self):
        super().__init__('add_vectors.json', ['in1', 'in2', 'out'])


class ScaleVectorNode(Node):
    def __init__(self):
        super().__init__('scale_vector.json', ['in1', 'in2', 'out'])


class SubtractVectorsNode(Node):
    def __init__(self):
        super().__init__('subtract_vectors.json', ['in1', 'in2', 'out'])


class DistanceNode(Node):
    def __init__(self):
        super().__init__('distance.json', ['in1', 'in2', 'out'])


class ConditionalVectorNode(Node):
    def __init__(self):
        super().__init__('conditional_set_vector.json', ['in1', 'in2', 'cond', 'out'])


class MagnitudeNode(Node):
    def __init__(self):
        super().__init__('magnitude.json', ['in', 'out'])


class NormalizeNode(Node):
    def __init__(self):
        super().__init__('normalize.json', ['in', 'out'])


# =========== DEBUG ==========
class DebugNode(Node):
    def __init__(self):
        super().__init__('debug.json', ['in'])
        self.is_terminated = True


class DrawLineNode(Node):
    def __init__(self):
        super().__init__('draw_line.json', ['start', 'end', 'thick', 'color'])
        self.is_terminated = True


class DrawDiscNode(Node):
    def __init__(self):
        super().__init__('draw_disc.json', ['pos', 'radius', 'thick', 'color'])
        self.is_terminated = True


# =========== OTHER ===========

class ColorNode(Node):
    def __init__(self, color: str):
        color = color.replace('_', ' ').title()
        super().__init__('color.json', ['out'], {'color': color})
        
        
class CountryNode(Node):
    def __init__(self, country: str):
        super().__init__('country.json', ['out'], {'value': country})


class StringNode(Node):
    def __init__(self, string: str):
        super().__init__('string.json', ['out'], {'value': string})
        
        
class StatNode(Node):
    def __init__(self, value):
        super().__init__('stat.json', ['out'], {'value': value})


# =========== SLIME ===========

class SlimeControllerNode(Node):
    def __init__(self):
        super().__init__('slime_controller.json', ['move', 'jump'])
        self.is_terminated = True


class VolleyballGetBoolNode(Node):
    def __init__(self, name):
        names = ['$self_can_jump', '$opponent_can_jump', '$ball_is_self_side']
        n = names.index(name)
        super().__init__('volleyball_get_bool.json', ['out'], {'name': n})


class VolleyballGetFloatNode(Node):
    def __init__(self, name):
        names = ['$delta_time', '$fixed_delta_time', '$gravity', '$pi', '$simulation_duration', '$team_score',
                 '$opponent_score', '$touches_remain']
        n = names.index(name)
        super().__init__('volleyball_get_float.json', ['out'], {'name': n})


class VolleyballGetVec3Node(Node):
    def __init__(self, name):
        names = ['$self_position', '$self_velocity', '$ball_position', '$ball_velocity',
                 '$opponent_position', '$opponent_velocity']
        n = names.index(name)
        super().__init__('volleyball_get_vec3.json', ['out'], {'name': n})


class ConstructSlimeNode(Node):
    def __init__(self):
        super().__init__('slime_construct.json', ['name', 'country', 'speed', 'accel', 'jump', 'color'])
        self.is_terminated = True

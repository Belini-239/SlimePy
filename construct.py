from generator.ast_nodes import *
from generator.functions_list import *
from generator.reserved_idents import ReservedRegister
from generator.variables import VarsManager, Variable
from optimizer import Optimizer


class Constructor:

    def __init__(self):
        self.graph = Graph()
        BuiltInRegister.set_graph(self.graph)
        self.vars_manager = VarsManager()

        self.optimization_dict = {}

    def full_construct(self, main_node, global_scope):
        reserved_out = ReservedRegister.get_out_list()
        for var in reserved_out:
            self.vars_manager.add_var(Variable(var['name'], None, var['type']))

        global_in = {}
        for dec in global_scope:
            for name in dec.names:
                if dec.var_type == 'number':
                    tmp = ns.AddFloatsNode()
                if dec.var_type == 'vec3':
                    tmp = ns.AddVectorsNode()
                if dec.var_type == 'bool':
                    tmp = ns.CompareBoolsNode('or')
                self.graph.add_node(tmp)
                global_in[name] = tmp.ports['in1']
                self.vars_manager.add_var(Variable(name, tmp.ports['out'], dec.var_type))

        self.construct(main_node)

        vars_stamp = self.vars_manager.get_stamp()
        vars_dict = {}
        for name, var in vars_stamp.items():
            if var.sid and name[0] == '$':
                vars_dict[name] = var.sid
        ReservedRegister.fill_out(vars_dict, self.graph)

        for dec in global_scope:
            for name in dec.names:
                self.graph.add_edge(vars_stamp[name].sid, global_in[name])



    def construct(self, node):

        if isinstance(node, Block):
            index = self.vars_manager.cur_index
            for stmt in node.statements:
                self.construct(stmt)
            self.vars_manager.pop_suf(index)

        elif isinstance(node, Declaration):
            self.construct(node.expr)
            if node.var_type != node.expr.type:
                raise Exception("Types are not equal (" + node.name + " " + node.var_type + " " + node.expr.type + ")")
            var = Variable(node.name, node.expr.SID, node.var_type)
            self.vars_manager.add_var(var)

        elif isinstance(node, Assignment):
            self.construct(node.expr)
            var = self.vars_manager.get_var(node.name)
            if not var:
                raise Exception("Unknown variable name (" + node.name + ")")
            if var.type != node.expr.type:
                raise Exception("Types are not equal (" + node.name + " " + var.type + " " + node.expr.type + ")")
            var.sid = node.expr.SID

        elif isinstance(node, Print):
            self.construct(node.expr)

            tmp = ns.DebugNode()
            self.graph.add_node(tmp)
            self.graph.add_edge(node.expr.SID, tmp.ports['in'])

        elif isinstance(node, If):
            self.construct(node.condition)
            if node.condition.type != "bool":
                raise Exception("Condition should be boolean")

            stamp = self.vars_manager.get_stamp()
            self.construct(node.true_block)
            stamp_ = self.vars_manager.get_stamp()

            change_names = []
            for k, v in stamp.items():
                if v.sid != stamp_[k].sid:
                    change_names.append(k)

            for name in change_names:
                tmp = None
                var = self.vars_manager.get_var(name)
                if var.type == 'number':
                    tmp = ns.ConditionalFloatNode()
                if var.type == 'vec3':
                    tmp = ns.ConditionalVectorNode()
                if tmp:
                    self.graph.add_node(tmp)
                    var_else = stamp[name].sid
                    var_if = stamp_[name].sid
                    self.graph.add_edge(var_if, tmp.ports['in1'])
                    self.graph.add_edge(var_else, tmp.ports['in2'])
                    self.graph.add_edge(node.condition.SID, tmp.ports['cond'])
                    var.sid = tmp.ports['out']
                else:
                    if var.type == 'bool':
                        or1 = ns.CompareBoolsNode('or')
                        and1 = ns.CompareBoolsNode('and')
                        and2 = ns.CompareBoolsNode('and')
                        inv1 = ns.NotNode()

                        var_else = stamp[name].sid
                        var_if = stamp_[name].sid

                        self.graph.add_node(or1)
                        self.graph.add_node(and1)
                        self.graph.add_node(and2)
                        self.graph.add_node(inv1)

                        self.graph.add_edge(node.condition.SID, and1.ports['in1'])
                        self.graph.add_edge(node.condition.SID, inv1.ports['in'])
                        self.graph.add_edge(inv1.ports['out'], and2.ports['in1'])
                        self.graph.add_edge(and1.ports['out'], or1.ports['in1'])
                        self.graph.add_edge(and2.ports['out'], or1.ports['in2'])

                        self.graph.add_edge(var_if, and1.ports['in2'])
                        self.graph.add_edge(var_else, and2.ports['in2'])

                        var.sid = or1.ports['out']

        elif isinstance(node, BinaryOp):
            self.construct(node.left)
            self.construct(node.right)

            tmp = None
            if node.op in ['+', '-', '/', '*'] and node.left.type == 'number' and node.right.type == 'number':
                node.type = 'number'
                if node.op == '+':
                    tmp = ns.AddFloatsNode()
                elif node.op == '/':
                    tmp = ns.DivideFloatsNode()
                elif node.op == '-':
                    tmp = ns.SubtractFloatsNode()
                elif node.op == '*':
                    tmp = ns.MultiplyFloatsNode()

            elif node.op in ['+', '-', '^'] and node.left.type == 'vec3' and node.right.type == 'vec3':
                node.type = 'vec3'
                if node.op == '+':
                    tmp = ns.AddVectorsNode()
                elif node.op == '-':
                    tmp = ns.SubtractVectorsNode()
                elif node.op == '^':
                    tmp = ns.CrossProductNode()

            elif node.op == '*' and node.left.type == 'vec3' and node.right.type == 'vec3':
                node.type = 'number'
                tmp = ns.DotProductNode()

            elif node.op == '*' and 'vec3' in [node.left.type, node.right.type] and 'number' in [node.left.type,
                                                                                                 node.right.type]:
                node.type = 'vec3'
                if node.left.type == 'number':
                    node.left, node.right = node.right, node.left
                tmp = ns.ScaleVectorNode()

            elif node.op in ['==', '<', '>', '<=', '>='] and node.left.type == node.right.type == 'number':
                node.type = 'bool'
                tmp = ns.CompareFloatsNode(node.op)

            elif node.op in ['and', 'or', '==', 'xor', 'xnor', 'nor',
                             'nand'] and node.left.type == node.right.type == 'bool':
                node.type = 'bool'
                op = node.op
                if op == '==':
                    op = 'eq'
                tmp = ns.CompareBoolsNode(op)

            else:
                raise Exception("Bad binary operation: " + node.left.type + " " + node.op + " " + node.right.type)

            if tmp:
                tmp = Optimizer.add_node(self.graph, tmp, {'in1': node.left.SID, 'in2': node.right.SID})
                node.SID = tmp.ports['out']

            # TODO

        elif isinstance(node, UnaryOp):

            if node.op == 'not':
                self.construct(node.expr)
                node.type = 'bool'
                if node.expr.type != 'bool':
                    raise Exception(f'Ban unary operation: {node.op} {node.type}')

                tmp = Optimizer.add_node(self.graph, ns.NotNode(), {'in': node.expr.SID})
                node.SID = tmp.ports['out']

            if node.op == '-':
                if isinstance(node.expr, Number):
                    value = node.expr.value * -1

                    tmp = Optimizer.add_node(self.graph, ns.FloatNode(float(value)), {})
                    node.SID = tmp.ports['out']
                    node.type = 'number'
                else:
                    self.construct(node.expr)
                    if node.expr.type == 'number':
                        tmp = Optimizer.add_node(self.graph, ns.SubtractFloatsNode(), {'in2': node.expr.SID})
                        node.SID = tmp.ports['out']
                        node.type = 'number'
                    elif node.expr.type == 'vec3':
                        tmp = Optimizer.add_node(self.graph, ns.SubtractVectorsNode(), {'in2': node.expr.SID})
                        node.SID = tmp.ports['out']
                        node.type = 'vec3'
                    else:
                        raise Exception(f'Ban unary operation: {node.op} {node.type}')

        elif isinstance(node, Vec3):
            self.construct(node.x)
            self.construct(node.y)
            self.construct(node.z)

            tmp = Optimizer.add_node(self.graph, ns.VectorNode(), {'x': node.x.SID, 'y': node.y.SID, 'z': node.z.SID})
            node.SID = str(tmp.ports['out'])
            node.type = 'vec3'

        elif isinstance(node, VectorComponent):
            self.construct(node.vector)

            tmp = Optimizer.add_node(self.graph, ns.SplitVectorNode(), {'in': node.vector.SID})
            node.SID = tmp.ports[node.component]
            node.type = 'number'

        elif isinstance(node, Number):
            tmp = Optimizer.add_node(self.graph, ns.FloatNode(float(node.value)), {})
            node.SID = tmp.ports['out']
            node.type = 'number'

        elif isinstance(node, Boolean):
            tmp = Optimizer.add_node(self.graph, ns.BoolNode(bool(node.value)), {})
            node.SID = tmp.ports['out']
            node.type = 'bool'

        elif isinstance(node, Identifier):
            var = self.vars_manager.get_var(node.name)
            if not var:
                raise Exception("Unknown variable name (" + node.name + ")")
            node.SID = str(var.sid)
            node.type = var.type

        elif isinstance(node, FunctionCall):
            for arg in node.args:
                self.construct(arg)
            BuiltInRegister.call(node.name, node.args, node)

        elif isinstance(node, StringLiteral):
            # TODO
            pass

        elif isinstance(node, ReservedIdentifier):
            var = ReservedRegister.get(node.name, self.graph)
            node.SID = var.SID
            node.type = var.type

        elif isinstance(node, Color):
            node.type = 'color'
            tmp = Optimizer.add_node(self.graph, ns.ColorNode(node.color), {})
            node.SID = tmp.ports['out']

        else:
            print(f"Unknown node: {type(node)}")

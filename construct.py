from generator.ast_nodes import *
from generator.functions_list import *
from generator.reserved_idents import ReservedRegister
from generator.variables import VarsManager, Variable


class Constructor:

    def __init__(self):
        self.graph = Graph()
        BuiltInRegister.set_graph(self.graph)
        self.vars_manager = VarsManager()

        self.numbers_dict = {}
        self.booleans_dict = {}
        self.vectors_splits_dict = {}
        self.colors_dict = {}

        reserved_out = ReservedRegister.get_out_list()
        for var in reserved_out:
            self.vars_manager.add_var(Variable(var['name'], None, var['type']))

    def full_construct(self, node):
        reserved_out = ReservedRegister.get_out_list()
        for var in reserved_out:
            self.vars_manager.add_var(Variable(var['name'], None, var['type']))

        self.construct(node)

        vars_stamp = self.vars_manager.get_stamp()
        vars_dict = {}
        for name, var in vars_stamp.items():
            if var.sid:
                vars_dict[name] = var.sid
        ReservedRegister.fill_out(vars_dict, self.graph)

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

            elif node.op in ['and', 'or', '==', 'xor', 'xnor', 'nor', 'nand'] and node.left.type == node.right.type == 'bool':
                node.type = 'bool'
                op = node.op
                if op == '==':
                    op = 'eq'
                tmp = ns.CompareBoolsNode(op)

            else:
                raise Exception("Bad binary operation: " + node.left.type + " " + node.op + " " + node.right.type)

            if tmp:
                self.graph.add_node(tmp)
                self.graph.add_edge(node.left.SID, tmp.ports['in1'])
                self.graph.add_edge(node.right.SID, tmp.ports['in2'])
                node.SID = tmp.ports['out']

            # TODO

        elif isinstance(node, UnaryOp):

            if node.op == 'not':
                self.construct(node.expr)
                node.type = 'bool'
                if node.expr.type != 'bool':
                    raise Exception(f'Ban unary operation: {node.op} {node.type}')
                tmp = ns.NotNode()
                node.SID = tmp.ports['out']
                self.graph.add_node(tmp)
                self.graph.add_edge(node.expr.SID, tmp.ports['in'])

            if node.op == '-':
                if isinstance(node.expr, Number):
                    value = node.expr.value * -1

                    if value not in self.numbers_dict:
                        tmp = ns.FloatNode(float(value))
                        self.numbers_dict[value] = tmp.ports['out']
                        self.graph.add_node(tmp)
                    node.SID = str(self.numbers_dict[value])
                    node.type = 'number'
                else:
                    self.construct(node.expr)
                    if node.expr.type == 'number':
                        tmp = ns.SubtractFloatsNode()
                        self.graph.add_node(tmp)
                        self.graph.add_edge(node.expr.SID, tmp.ports['in2'])
                        node.SID = tmp.ports['out']
                        node.type = 'number'
                    elif node.expr.type == 'vec3':
                        tmp = ns.SubtractVectorsNode()
                        self.graph.add_node(tmp)
                        self.graph.add_edge(node.expr.SID, tmp.ports['in2'])
                        node.SID = tmp.ports['out']
                        node.type = 'vec3'
                    else:
                        raise Exception(f'Ban unary operation: {node.op} {node.type}')

        elif isinstance(node, Vec3):
            self.construct(node.x)
            self.construct(node.y)
            self.construct(node.z)

            tmp = ns.VectorNode()
            node.SID = str(tmp.ports['out'])
            node.type = 'vec3'
            self.graph.add_node(tmp)
            self.graph.add_edge(node.x.SID, tmp.ports['x'])
            self.graph.add_edge(node.y.SID, tmp.ports['y'])
            self.graph.add_edge(node.z.SID, tmp.ports['z'])

        elif isinstance(node, VectorComponent):
            self.construct(node.vector)

            if node.vector.SID not in self.vectors_splits_dict:
                tmp = ns.SplitVectorNode()
                self.graph.add_node(tmp)
                self.graph.add_edge(node.vector.SID, tmp.ports['in'])
                self.vectors_splits_dict[node.vector.SID] = tmp

            node.SID = self.vectors_splits_dict[node.vector.SID].ports[node.component]
            node.type = 'number'

        elif isinstance(node, Number):
            if node.value not in self.numbers_dict:
                tmp = ns.FloatNode(float(node.value))
                self.numbers_dict[node.value] = tmp.ports['out']
                self.graph.add_node(tmp)
            node.SID = str(self.numbers_dict[node.value])
            node.type = 'number'

        elif isinstance(node, Boolean):
            if node.value not in self.booleans_dict:
                tmp = ns.BoolNode(bool(node.value))
                self.booleans_dict[node.value] = tmp.ports['out']
                self.graph.add_node(tmp)
            node.SID = str(self.booleans_dict[node.value])
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
            if node.color not in self.colors_dict:
                tmp = ns.ColorNode(node.color)
                self.colors_dict[node.color] = tmp.ports['out']
                self.graph.add_node(tmp)
            node.SID = self.colors_dict[node.color]

        else:
            print(f"Unknown node: {type(node)}")

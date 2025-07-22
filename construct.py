from generator.ast_nodes import *
from generator.functions_list import *
from generator.reserved_idents import ReservedRegister
from generator.variables import VarsManager, Variable
from optimizer import Optimizer
from error_handler import ErrorHandler


class Constructor:

    def __init__(self):
        self.graph = Graph()
        BuiltInRegister.set_graph(self.graph)
        self.global_vars = VarsManager()
        self.cur_scopes = []

        self.optimization_dict = {}

    def full_construct(self, main_node, global_scope):
        reserved_out = ReservedRegister.get_out_list()
        for var in reserved_out:
            self.global_vars.add_var(Variable(var['name'], None, var['type']))

        global_in = {}
        for dec in global_scope:
            if isinstance(dec, GlobalDeclaration):
                for name in dec.names:
                    if dec.var_type == 'number':
                        tmp = ns.AddFloatsNode()
                    if dec.var_type == 'vec3':
                        tmp = ns.AddVectorsNode()
                    if dec.var_type == 'bool':
                        tmp = ns.CompareBoolsNode('or')
                    self.graph.add_node(tmp)
                    global_in[name] = tmp.ports['in1']
                    self.global_vars.add_var(Variable(name, tmp.ports['out'], dec.var_type))
            elif isinstance(dec, FunctionDefinition):
                print(dec.name, dec.args, dec.return_type)
                BuiltInRegister.register_custom(dec.name, dec.args, dec.return_type, dec.block)

        self.construct(main_node, VarsManager())

        vars_stamp = self.global_vars.get_stamp()
        vars_dict = {}
        for name, var in vars_stamp.items():
            if var.sid and name[0] == '$':
                vars_dict[name] = var.sid
        ReservedRegister.fill_out(vars_dict, self.graph)

        for dec in global_scope:
            if isinstance(dec, GlobalDeclaration):
                for name in dec.names:
                    self.graph.add_edge(vars_stamp[name].sid, global_in[name])

    def get_vars_stamp(self, local_vars: VarsManager):
        local_stamp = local_vars.get_stamp()
        global_stamp = self.global_vars.get_stamp()
        res_stamp = global_stamp
        for name, val in local_stamp.items():
            res_stamp[name] = val
        return res_stamp

    def get_var(self, local_vars: VarsManager, name):
        var = local_vars.get_var(name)
        if var is None:
            var = self.global_vars.get_var(name)
        if var is None:
            raise Exception("Unknown variable name (" + name + ")")
        return var

    def conditional_set(self, var_if, var_else, var_cond, var_type):
        tmp = None
        if var_type == 'number':
            tmp = ns.ConditionalFloatNode()
        if var_type == 'vec3':
            tmp = ns.ConditionalVectorNode()
        if tmp:
            tmp = Optimizer.add_node(self.graph, tmp, {'in1': var_if, 'in2': var_else, 'cond': var_cond})
            return tmp.ports['out']
        else:
            if var_type == 'bool':
                inv1 = Optimizer.add_node(self.graph, ns.NotNode(), {'in': var_cond})
                and1 = Optimizer.add_node(self.graph, ns.CompareBoolsNode('and'), {'in1': var_cond, 'in2': var_if})
                and2 = Optimizer.add_node(self.graph, ns.CompareBoolsNode('and'), {'in1': inv1.ports['out'], 'in2': var_else})
                or1 = Optimizer.add_node(self.graph, ns.CompareBoolsNode('or'), {'in1': and1.ports['out'], 'in2': and2.ports['out']})
                return or1.ports['out']

    def construct(self, node, local_vars: VarsManager):
        try:
            if isinstance(node, Block):
                index = local_vars.cur_index
                for stmt in node.statements:
                    self.construct(stmt, local_vars)
                local_vars.pop_suf(index)

            elif isinstance(node, Declaration):
                self.construct(node.expr, local_vars)
                if node.var_type != node.expr.type:
                    ErrorHandler.error(
                        "Types are not equal (" + node.name + ": " + node.var_type + ", " + node.expr.type + ")",
                        node.token)
                var = Variable(node.name, node.expr.SID, node.var_type)
                local_vars.add_var(var)

            elif isinstance(node, Assignment):
                self.construct(node.expr, local_vars)
                var = local_vars.get_var(node.name)
                if var is None:
                    var = self.global_vars.get_var(node.name)
                if not var:
                    ErrorHandler.error("Unknown variable name (" + node.name + ")", node.token)
                if var.type != node.expr.type:
                    ErrorHandler.error(
                        "Types are not equal (" + node.name + ": " + var.type + ", " + node.expr.type + ")",
                        node.token)
                var.sid = node.expr.SID

            elif isinstance(node, Print):
                self.construct(node.expr, local_vars)

                tmp = ns.DebugNode()
                self.graph.add_node(tmp)
                self.graph.add_edge(node.expr.SID, tmp.ports['in'])

            elif isinstance(node, If):
                self.construct(node.condition, local_vars)
                if node.condition.type != "bool":
                    ErrorHandler.error("Condition should be boolean", node.token)

                stamp = self.get_vars_stamp(local_vars)
                self.construct(node.true_block, local_vars)
                stamp_ = self.get_vars_stamp(local_vars)

                change_names = []
                for k, v in stamp.items():
                    if v.sid != stamp_[k].sid:
                        change_names.append(k)

                for name in change_names:
                    var = self.get_var(local_vars, name)
                    res_sid = self.conditional_set(stamp_[name].sid, stamp[name].sid, node.condition.SID, var.type)
                    var.sid = res_sid

            elif isinstance(node, BinaryOp):
                self.construct(node.left, local_vars)
                self.construct(node.right, local_vars)

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
                    ErrorHandler.error(
                        "Bad binary operation: " + node.left.type + " " + node.op + " " + node.right.type, node.token)

                if tmp:
                    tmp = Optimizer.add_node(self.graph, tmp, {'in1': node.left.SID, 'in2': node.right.SID})
                    node.SID = tmp.ports['out']

            elif isinstance(node, UnaryOp):

                if node.op == 'not':
                    self.construct(node.expr, local_vars)
                    node.type = 'bool'
                    if node.expr.type != 'bool':
                        ErrorHandler.error(f'Ban unary operation: {node.op} {node.type}', node.token)

                    tmp = Optimizer.add_node(self.graph, ns.NotNode(), {'in': node.expr.SID})
                    node.SID = tmp.ports['out']

                if node.op == '-':
                    if isinstance(node.expr, Number):
                        value = node.expr.value * -1

                        tmp = Optimizer.add_node(self.graph, ns.FloatNode(float(value)), {})
                        node.SID = tmp.ports['out']
                        node.type = 'number'
                    else:
                        self.construct(node.expr, local_vars)
                        if node.expr.type == 'number':
                            tmp = Optimizer.add_node(self.graph, ns.SubtractFloatsNode(), {'in2': node.expr.SID})
                            node.SID = tmp.ports['out']
                            node.type = 'number'
                        elif node.expr.type == 'vec3':
                            tmp = Optimizer.add_node(self.graph, ns.SubtractVectorsNode(), {'in2': node.expr.SID})
                            node.SID = tmp.ports['out']
                            node.type = 'vec3'
                        else:
                            ErrorHandler.error(f'Ban unary operation: {node.op} {node.type}', node.token)

            elif isinstance(node, Vec3):
                self.construct(node.x, local_vars)
                self.construct(node.y, local_vars)
                self.construct(node.z, local_vars)

                tmp = Optimizer.add_node(self.graph, ns.VectorNode(),
                                         {'x': node.x.SID, 'y': node.y.SID, 'z': node.z.SID})
                node.SID = str(tmp.ports['out'])
                node.type = 'vec3'

            elif isinstance(node, VectorComponent):
                self.construct(node.vector, local_vars)

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
                var = self.get_var(local_vars, node.name)
                if not var:
                    ErrorHandler.error("Unknown variable name (" + node.name + ")", node.token)
                node.SID = str(var.sid)
                node.type = var.type

            elif isinstance(node, FunctionCall):
                for arg in node.args:
                    self.construct(arg, local_vars)
                if BuiltInRegister.check_builtin_function(node.name):
                    BuiltInRegister.call(node.name, node.args, node)
                else:
                    func = BuiltInRegister.get_function(node.name, node.args)
                    if func.name in self.cur_scopes:
                        raise Exception('Recursion is prohibited')
                    self.cur_scopes.append(func.name)
                    func_local_vars = VarsManager()
                    for i in range(len(func.args_names)):
                        func_local_vars.add_var(Variable(func.args_names[i], node.args[i].SID, func.args[i]))
                    func_local_vars.add_var(Variable('$return', None, func.return_type))

                    self.construct(func.block, func_local_vars)

                    self.cur_scopes.pop()
                    return_var = func_local_vars.get_var('$return')
                    node.type = func.return_type
                    node.SID = return_var.sid

            elif isinstance(node, StringLiteral):
                node.type = 'str'
                tmp = Optimizer.add_node(self.graph, ns.StringNode(node.value), {})
                node.SID = tmp.ports['out']

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

        except Exception as e:
            ErrorHandler.error(str(e), node.token)

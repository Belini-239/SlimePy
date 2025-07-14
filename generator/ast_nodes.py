from builder.graph import Graph


class Node:
    def __init__(self):
        self.type = "unknown"
        self.SID = ""


class Number(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"


class Boolean(Node):
    def __init__(self, value):
        self.value = value
        super().__init__()

    def __repr__(self):
        return f"Boolean({self.value})"


class Vec3(Node):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        super().__init__()

    def __repr__(self):
        return f"Vec3({self.x}, {self.y}, {self.z})"


class VectorComponent(Node):
    def __init__(self, vector, component):
        self.vector = vector
        self.component = component
        super().__init__()

    def __repr__(self):
        return f"VectorComponent({self.vector}, {self.component})"


class StringLiteral(Node):
    def __init__(self, value):
        self.value = value
        super().__init__()

    def __repr__(self):
        return f"String('{self.value}')"


class Identifier(Node):
    def __init__(self, name, var_type=None):
        self.name = name
        super().__init__()

    def __repr__(self):
        type_str = f" : {self.type}" if self.type else ""
        return f"Identifier('{self.name}'{type_str})"


class Color(Node):
    def __init__(self, color):
        self.color = color
        super().__init__()

    def __repr__(self):
        return f"Color('{self.color})"


class ReservedIdentifier(Node):
    def __init__(self, name, var_type=None):
        self.name = name
        super().__init__()

    def __repr__(self):
        type_str = f" : {self.type}" if self.type else ""
        return f"Reserved identifier('{self.name}'{type_str})"


class BinaryOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        super().__init__()

    def __repr__(self):
        return f"BinaryOp({self.op},\n  left={self.left},\n  right={self.right})"


class UnaryOp(Node):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
        super().__init__()

    def __repr__(self):
        return f"UnaryOp({self.op},\n  expr={self.expr})"


class Declaration(Node):
    def __init__(self, name, var_type, expr):
        self.name = name
        self.var_type = var_type
        self.expr = expr
        super().__init__()

    def __repr__(self):
        return f"Declaration(\n  name='{self.name}',\n  type='{self.var_type}',\n  expr={self.expr})"


class Assignment(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
        super().__init__()

    def __repr__(self):
        return f"Assignment(\n  name='{self.name}',\n  expr={self.expr})"


class Print(Node):
    def __init__(self, expr):
        self.expr = expr
        super().__init__()

    def __repr__(self):
        return f"Print(\n  expr={self.expr})"


class If(Node):
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block
        super().__init__()

    def __repr__(self):
        false_repr = f"\n  false={self.false_block}" if self.false_block else ""
        return f"If(\n  condition={self.condition},\n  true={self.true_block}{false_repr})"


class While(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block
        super().__init__()

    def __repr__(self):
        return f"While(\n  condition={self.condition},\n  block={self.block})"


class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args
        super().__init__()

    def __repr__(self):
        return f"FunctionCall(\n  name={self.name},\n  args={self.args})"


class Block(Node):
    def __init__(self, statements):
        self.statements = statements
        super().__init__()

    def __repr__(self):
        stmts = "\n".join([f"  {i + 1}: {stmt}" for i, stmt in enumerate(self.statements)])
        return f"Block([\n{stmts}\n])"

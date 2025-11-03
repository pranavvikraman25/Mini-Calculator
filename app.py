import streamlit as st
import ast
import operator as op
import math

# allowed binary operators
BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.LShift: op.lshift,
    ast.RShift: op.rshift,
}

# allowed unary operators
UNARY_OPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
    ast.Invert: op.invert,
}

# allowed math functions and constants
NAMES = {name: getattr(math, name) for name in (
    'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
    'sinh', 'cosh', 'tanh', 'sqrt', 'log', 'log10',
    'exp', 'degrees', 'radians', 'floor', 'ceil', 'fabs'
)}
NAMES.update({'pi': math.pi, 'e': math.e, 'abs': abs, 'pow': pow})

class SafeEval(ast.NodeVisitor):
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def visit_Module(self, node):
        if len(node.body) != 1:
            raise ValueError("Only single expressions allowed")
        return self.visit(node.body[0])

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers are allowed")

    def visit_Num(self, node):
        return node.n

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type in BIN_OPS:
            return BIN_OPS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator {op_type}")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type in UNARY_OPS:
            return UNARY_OPS[op_type](operand)
        raise ValueError(f"Unsupported unary operator {op_type}")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct function calls allowed")
        func_name = node.func.id
        if func_name not in NAMES:
            raise ValueError(f"Use of function '{func_name}' is not allowed")
        func = NAMES[func_name]
        args = [self.visit(a) for a in node.args]
        return func(*args)

    def visit_Name(self, node):
        if node.id in NAMES:
            return NAMES[node.id]
        raise ValueError(f"Unknown name: {node.id}")

    def generic_visit(self, node):
        raise ValueError(f"Unsupported syntax: {node.__class__.__name__}")

def evaluate(expr):
    try:
        tree = ast.parse(expr, mode='exec')
        return SafeEval().visit(tree)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

# --- Streamlit UI ---
st.title("🧮 Safe Math Calculator")
st.write("Enter expressions like `2+2`, `3*sqrt(2)`, `sin(pi/2)`, `pow(2,3)`")

expr = st.text_input("Expression:")

if expr:
    try:
        result = evaluate(expr)
        st.success(f"Result: {result}")
    except ValueError as e:
        st.error(e)

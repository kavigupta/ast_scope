
import ast
from ast_scope.annotate import annotate
from ast_scope.scope import GlobalScope, ErrorScope, FunctionScope, ClassScope

def description_of_node(node):
    if type(node).__name__ == "Name":
        name = node.id
    elif type(node).__name__ == "arg":
        name = node.arg
    elif type(node).__name__ in ["FunctionDef", "AsyncFunctionDef"]:
        name = node.name
    else:
        raise RuntimeError(f"Unsupported node type: {node}")
    return f"{name}@{node.lineno}:{node.col_offset}"

def description_of_scope(scope):
    if isinstance(scope, GlobalScope):
        return 'global'
    if isinstance(scope, ErrorScope):
        return 'error'
    if isinstance(scope, FunctionScope):
        return f'function[{description_of_node(scope.function_node)}]'
    if isinstance(scope, ClassScope):
        return f'class[{description_of_node(scope.class_scope)}]'
    raise RuntimeError(f"Unsupported node type: {scope}")

def classify_all(code):
    tree = ast.parse(code)
    _, _, mapping = annotate(tree)
    return {description_of_node(node) : description_of_scope(scope) for node, scope in mapping.items()}

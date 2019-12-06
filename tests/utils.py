
import unittest
import ast
import re

from ast_scope.annotate import annotate
from ast_scope.scope import GlobalScope, ErrorScope, FunctionScope, ClassScope

def get_name(node):
    if type(node).__name__ == "Name":
        name = node.id
    elif type(node).__name__ == "arg":
        name = node.arg
    elif type(node).__name__ in ["FunctionDef", "AsyncFunctionDef"]:
        name = node.name
    else:
        raise RuntimeError(f"Unsupported node type: {node}")
    return name

def description_of_node(node):
    name = get_name(node)
    return f"{name}@{node.lineno}:{node.col_offset}"

def description_of_scope(scope):
    if isinstance(scope, GlobalScope):
        return 'g'
    if isinstance(scope, ErrorScope):
        return '?'
    if isinstance(scope, FunctionScope):
        return f'~{description_of_node(scope.function_node)}'
    if isinstance(scope, ClassScope):
        return f'-{description_of_node(scope.class_scope)}'
    raise RuntimeError(f"Unsupported node type: {scope}")

def display_annotated(code):
    lines = [list(x) for x in code.split("\n")]
    tree = ast.parse(code)
    _, _, mapping = annotate(tree)
    for node, scope in mapping.items():
        scope_description = description_of_scope(scope)
        lines[node.lineno-1][node.col_offset] = "{" + scope_description + "}" + lines[node.lineno-1][node.col_offset]
    return "\n".join("".join(x) for x in lines)

def trim(docstring):
    #  slightly modified from https://stackoverflow.com/a/2504457/1549476
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = float('inf')
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < float('inf'):
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)

def all_nodes_gen_for_scope(scope):
    if hasattr(scope, 'children'):
        for child_scope in scope.children:
            yield from all_nodes_gen_for_scope(child_scope)
    yield from scope.variables.variables
    yield from scope.variables.functions
    yield from scope.variables.classes
    yield from scope.variables.import_statements

class DisplayAnnotatedTestCase(unittest.TestCase):
    def assertAnnotationWorks(self, annotated_code):
        code = trim(re.sub(r"\{[^\}]+\}", "", annotated_code))

        global_scope, error_scope, mapping = annotate(ast.parse(code))
        variables = list(all_nodes_gen_for_scope(global_scope)) + list(all_nodes_gen_for_scope(error_scope))
        self.assertCountEqual(variables, list(mapping))

        self.assertEqual(
            display_annotated(code),
            trim(annotated_code)
        )

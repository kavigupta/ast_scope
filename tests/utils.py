
import sys
import ast
import re
import unittest

from ast_scope.annotate import annotate
from ast_scope.scope import GlobalScope, ErrorScope, FunctionScope, ClassScope

def get_name(node):
    pos_info_node = node
    if type(node).__name__ == "Name":
        name = node.id
    elif type(node).__name__ == "arg":
        name = node.arg
    elif type(node).__name__ in ["FunctionDef", "AsyncFunctionDef"]:
        name = node.name
    elif type(node).__name__ == "ClassDef":
        name = node.name
    elif type(node).__name__ == "Lambda":
        name = ""
    elif type(node).__name__ == "comprehension":
        name = ""
        pos_info_node = node.target
    else:
        raise RuntimeError("Unsupported node type: {node}".format(node=node))
    return name, pos_info_node

def description_of_node(node):
    name, pos = get_name(node)
    return "{name}@{lineno}:{col_offset}".format(name=name, lineno=pos.lineno, col_offset=pos.col_offset)

def description_of_scope(scope):
    if isinstance(scope, GlobalScope):
        return 'g'
    if isinstance(scope, ErrorScope):
        return '?'
    if isinstance(scope, FunctionScope):
        return '~' + description_of_node(scope.function_node)
    if isinstance(scope, ClassScope):
        return '-' + description_of_node(scope.class_node)
    raise RuntimeError("Unsupported node type: {scope}".format(scope=scope))

def display_annotated(code, class_binds_near):
    lines = [list(x) for x in code.split("\n")]
    tree = ast.parse(code)
    mapping = annotate(tree, class_binds_near)._node_to_containing_scope
    for node, scope in mapping.items():
        if not hasattr(node, "lineno"):
            continue
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

def all_nodes_gen_for_variables(variables):
    yield from variables.variables
    yield from variables.functions
    yield from variables.classes
    yield from variables.import_statements

def all_nodes_gen_for_scope(scope):
    if hasattr(scope, 'children'):
        for child_scope in scope.children:
            yield from all_nodes_gen_for_scope(child_scope)
    for node in all_nodes_gen_for_variables(scope.variables):
        yield scope, node

class DisplayAnnotatedTestCase(unittest.TestCase):
    def _check_nodes(self, mapping, *scopes):
        overall_scope = [item for scope in scopes for item in all_nodes_gen_for_scope(scope)]
        for scope, node in overall_scope:
            self.assertEqual(mapping[node], scope)
        self.assertCountEqual([node for _, node in overall_scope], list(mapping))

    def assertAnnotationWorks(self, annotated_code, code=None, *, class_binds_near=False):
        if code is None:
            code = trim(re.sub(r"\{[^\}]+\}", "", annotated_code))

        scope_info = annotate(ast.parse(code), class_binds_near)
        scope_info.static_dependency_graph # just check for errors
        self._check_nodes(scope_info._node_to_containing_scope, scope_info._global_scope, scope_info._error_scope)

        self.assertEqual(
            display_annotated(code, class_binds_near),
            trim(annotated_code)
        )

    def assertGraphWorks(self, code, vertices, edges):
        graph = annotate(ast.parse(trim(code))).static_dependency_graph
        self.assertCountEqual(graph.nodes(), vertices)
        self.assertCountEqual(graph.edges(), edges)


def create_condiitional_version(predicate):
    def conditional_version(*version):
        def decorator(original_test):
            def test(*args, **kwargs):
                if predicate(version):
                    original_test(*args, **kwargs)
            test.__name__ = original_test.__name__
            return test
        return decorator
    return conditional_version

from_version = create_condiitional_version(lambda version: sys.version_info >= version)
pre_version = create_condiitional_version(lambda version: sys.version_info < version)

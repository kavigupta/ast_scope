import ast

from .scope import GlobalScope, ErrorScope, FunctionScope, ClassScope
from .annotator import IntermediateGlobalScope, IntermediateFunctionScope, IntermediateClassScope

class PullScopes(ast.NodeVisitor):
    def __init__(self, annotation_dict):
        self.annotation_dict = annotation_dict
        self.node_to_scope = {}
        self.global_scope = GlobalScope()
        self.error_scope = ErrorScope()

    def convert(self, int_scope):
        if int_scope is None:
            return self.error_scope
        if isinstance(int_scope, IntermediateGlobalScope):
            return self.global_scope
        if int_scope.node in self.node_to_scope:
            return self.node_to_scope[int_scope.node]
        if isinstance(int_scope, IntermediateFunctionScope):
            scope = FunctionScope(int_scope.node)
        elif isinstance(int_scope, IntermediateClassScope):
            scope = ClassScope(scope.node)
        else:
            raise RuntimeError("unreachable")

        self.node_to_scope[int_scope.node] = scope
        return scope

    def pull_scope(self, node):
        name, intermediate_scope = self.annotation_dict[node]
        true_intermediate_scope = intermediate_scope.find(name)
        return self.convert(true_intermediate_scope)

    def visit_Name(self, node):
        scope = self.pull_scope(node)
        scope.add_variable(node)

    def visit_FunctionDef(self, node):
        scope = self.pull_scope(node)
        if node not in self.node_to_scope:
            self.node_to_scope[node] = FunctionScope(node)
        scope.add_function(node, self.node_to_scope[node])

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        scope = self.pull_scope(node)
        if node not in self.node_to_scope:
            self.node_to_scope[node] = ClassScope(node)
        scope.add_class(node, self.node_to_scope[node])

import ast

from ast_scope.scope import ErrorScope, FunctionScope, GlobalScope, Scope

from .annotator import AnnotateScope, IntermediateGlobalScope, IntermediateScope
from .graph import DiGraph
from .pull_scope import PullScopes
from .utils import get_all_nodes, get_name


class ScopeInfo:
    def __init__(
        self,
        tree: ast.AST,
        global_scope: GlobalScope,
        error_scope: ErrorScope,
        node_to_containing_scope: dict[ast.AST, Scope],
    ):
        self._tree = tree
        self._global_scope = global_scope
        self._error_scope = error_scope
        self._node_to_containing_scope = node_to_containing_scope

    @property
    def global_scope(self):
        return self._global_scope

    @property
    def static_dependency_graph(self):
        """
        Returns a static dependency graph of all the top-level functions and classes in the
            given piece of code.

        Note: this function assumes all top level code is original definitions
            and thus does not handle reassignment of functions or classes, or
            any other variables.
        """
        variables = self.global_scope.symbols_in_frame
        g = DiGraph()
        g.add_nodes_from(variables)
        varis = self.global_scope.variables
        for construct in varis.functions | varis.classes:
            for node in get_all_nodes(*construct.body):
                if node not in self:
                    continue
                if self[node] is not self._global_scope:
                    continue
                g.add_edge(get_name(construct), get_name(node))
        return g

    def __iter__(self):
        return iter(self._node_to_containing_scope)

    def __contains__(self, node: ast.AST):
        return node in self._node_to_containing_scope

    def __getitem__(self, node: ast.AST):
        return self._node_to_containing_scope[node]

    def function_scope_for(self, node: ast.AST):
        """
        Returns the function scope for the given FunctionDef node.
        """
        scopes = self._node_to_containing_scope.values()
        for scope in scopes:
            if not isinstance(scope, FunctionScope):
                continue
            if node == scope.function_node:
                return scope
        return None


def annotate(tree: ast.AST, class_binds_near: bool = False):
    annotation_dict: dict[ast.AST, tuple[str, IntermediateScope, bool]] = {}
    annotator = AnnotateScope(
        IntermediateGlobalScope(), annotation_dict, class_binds_near=class_binds_near
    )
    annotator.visit(tree)

    pull_scopes = PullScopes(annotation_dict)
    pull_scopes.visit(tree)
    return ScopeInfo(
        tree,
        pull_scopes.global_scope,
        pull_scopes.error_scope,
        pull_scopes.node_to_containing_scope,
    )

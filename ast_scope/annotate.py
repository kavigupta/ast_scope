from .annotator import AnnotateScope, IntermediateGlobalScope
from .pull_scope import PullScopes

class ScopeInfo:
    def __init__(self, tree, global_scope, error_scope, node_to_containing_scope):
        self._tree = tree
        self._global_scope = global_scope
        self._error_scope = error_scope
        self._node_to_containing_scope = node_to_containing_scope

    @property
    def global_scope(self):
        return self._global_scope

def annotate(tree, class_binds_near=False):
    annotation_dict = {}
    annotator = AnnotateScope(IntermediateGlobalScope(), annotation_dict, class_binds_near=class_binds_near)
    annotator.visit(tree)

    pull_scopes = PullScopes(annotation_dict)
    pull_scopes.visit(tree)
    return ScopeInfo(tree, pull_scopes.global_scope, pull_scopes.error_scope, pull_scopes.node_to_containing_scope)

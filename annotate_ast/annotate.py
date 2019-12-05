from .annotator import AnnotateScope, IntermediateGlobalScope
from .pull_scope import PullScopes


def annotate(tree):
    annotation_dict = {}
    annotator = AnnotateScope(IntermediateGlobalScope(), annotation_dict)
    annotator.visit(tree)

    pull_scopes = PullScopes(annotation_dict)
    pull_scopes.visit(tree)
    return pull_scopes.global_scope, pull_scopes.error_scope, pull_scopes.node_to_scope

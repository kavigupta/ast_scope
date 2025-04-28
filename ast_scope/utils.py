import ast

from .group_similar_constructs import GroupSimilarConstructsVisitor


class GetAllNodes(ast.NodeVisitor):
    def __init__(self):
        self.nodes = []

    def generic_visit(self, node):
        self.nodes.append(node)
        super().generic_visit(node)


def get_all_nodes(*nodes):
    getter = GetAllNodes()
    for node in nodes:
        getter.visit(node)
    nodes = set(nodes)
    return [subnode for subnode in getter.nodes if subnode not in nodes]


class GetName(GroupSimilarConstructsVisitor):
    def __init__(self):
        self.name = None

    def visit_Name(self, node):
        self.name = node.id

    def visit_function_def(self, func_node, is_async):
        self.name = func_node.name

    def visit_ClassDef(self, class_node):
        self.name = class_node.name

    def visit_alias(self, alias_node):
        self.name = name_of_alias(alias_node)


def get_name(node):
    getter = GetName()
    getter.visit(node)
    assert getter.name is not None
    return getter.name


def name_of_alias(alias_node):
    if alias_node.asname is not None:
        return alias_node.asname
    return alias_node.name


def compute_class_fields(class_node):
    """
    Compute the fields of a class node that are in the class scope, versus the parent scope.

    :returns: (class_fields, parent_fields)
        two lists containing the fields in the class scope and the parent scope, respectively.
    """
    assert class_node._fields == (
        "name",
        "bases",
        "keywords",
        "body",
        "decorator_list",
    )
    return [class_node.body], [
        class_node.bases,
        class_node.keywords,
        class_node.decorator_list,
    ]

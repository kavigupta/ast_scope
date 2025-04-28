from __future__ import annotations

import ast
from typing import List

from .group_similar_constructs import GroupSimilarConstructsVisitor


class GetAllNodes(ast.NodeVisitor):
    def __init__(self):
        self.nodes: list[ast.AST] = []

    def generic_visit(self, node: ast.AST):
        self.nodes.append(node)
        super().generic_visit(node)


def get_all_nodes(*nodes: List[ast.AST]):
    getter = GetAllNodes()
    for node in nodes:
        getter.visit(node)
    nodes = set(nodes)
    return [subnode for subnode in getter.nodes if subnode not in nodes]


class GetName(GroupSimilarConstructsVisitor):
    def __init__(self):
        self.name = None

    def visit_Name(self, node: ast.Name):
        self.name = node.id

    def visit_function_def(
        self, func_node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool
    ):
        self.name = func_node.name

    def visit_ClassDef(self, node: ast.ClassDef):
        self.name = node.name

    def visit_alias(self, node: ast.alias):
        self.name = name_of_alias(node)


def get_name(node: ast.AST):
    getter = GetName()
    getter.visit(node)
    assert getter.name is not None
    return getter.name


def name_of_alias(alias_node: ast.alias):
    if alias_node.asname is not None:
        return alias_node.asname
    return alias_node.name


def compute_class_fields(class_node):
    """
    Compute the fields of a class node that are in the class scope, versus the parent scope.

    :returns: (class_fields, parent_fields)
        two lists containing the fields in the class scope and the parent scope, respectively.
    """
    fields_in_all = ("name", "bases", "keywords", "body", "decorator_list")
    assert class_node._fields in (fields_in_all, fields_in_all + ("type_params",))
    class_fields = [class_node.body]
    parent_fields = [class_node.bases, class_node.keywords, class_node.decorator_list]
    if "type_params" in class_node._fields:
        class_fields.append(class_node.type_params)
    return class_fields, parent_fields

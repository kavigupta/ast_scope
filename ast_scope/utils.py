import ast

from .group_similar_constructs import GroupSimilarConstructsVisitor


class GetAllNodes(ast.NodeVisitor):
    def __init__(self):
        self.nodes: list[ast.AST] = []

    def generic_visit(self, node: ast.AST):
        self.nodes.append(node)
        super().generic_visit(node)


def get_all_nodes(node: ast.AST):
    getter = GetAllNodes()
    getter.visit(node)
    return [subnode for subnode in getter.nodes if subnode is not node]


class GetName(GroupSimilarConstructsVisitor):
    def __init__(self):
        self.name = None

    def visit_Name(self, node: ast.Name):
        self.name = node.id

    def visit_function_def(self, func_node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool): 
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

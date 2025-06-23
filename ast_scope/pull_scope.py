from __future__ import annotations

import ast
from typing import Union, cast

from ast_scope.utils import compute_class_fields

from .annotator import (
    IntermediateClassScope,
    IntermediateFunctionScope,
    IntermediateGlobalScope,
    IntermediateScope,
    visit_all,
)
from .group_similar_constructs import GroupSimilarConstructsVisitor
from .scope import ClassScope, ErrorScope, FunctionScope, GlobalScope, Scope


class PullScopes(GroupSimilarConstructsVisitor):
    def __init__(
        self, annotation_dict: dict[ast.AST, tuple[str, IntermediateScope, bool]]
    ):
        self.annotation_dict = annotation_dict
        self.node_to_corresponding_scope: dict[ast.AST, Scope] = {}
        self.node_to_containing_scope: dict[ast.AST, Scope] = {}
        self.global_scope = GlobalScope()
        self.error_scope = ErrorScope()

    def convert(self, int_scope: IntermediateScope | None):
        if int_scope is None:
            return self.error_scope
        if isinstance(int_scope, IntermediateGlobalScope):
            return self.global_scope
        int_scope = cast(
            Union[IntermediateClassScope, IntermediateFunctionScope], int_scope
        )
        return self.node_to_corresponding_scope[int_scope.node]

    def pull_scope(self, node: ast.AST, include_as_variable: bool = True) -> Scope:
        name, intermediate_scope, is_assign = self.annotation_dict[node]
        true_intermediate_scope = intermediate_scope.find(name, is_assign)
        scope = self.convert(true_intermediate_scope)
        if include_as_variable:
            self.node_to_containing_scope[node] = scope
        return scope

    def visit_Name(self, node: ast.Name):
        scope = self.pull_scope(node)
        scope.add_variable(node)
        super().generic_visit(node)

    def visit_arg(self, node: ast.arg):
        scope = self.pull_scope(node)
        scope.add_argument(node)
        super().generic_visit(node)

    def visit_alias(self, node: ast.alias):
        scope = self.pull_scope(node)
        scope.add_import(node)
        super().generic_visit(node)

    def visit_function_def(
        self, func_node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool
    ):
        del is_async
        scope = self.pull_scope(func_node)
        if func_node not in self.node_to_corresponding_scope:
            self.node_to_corresponding_scope[func_node] = FunctionScope(
                func_node, scope
            )
        scope.add_function(
            func_node,
            self.node_to_corresponding_scope[func_node],
            include_as_variable=True,
        )
        super().generic_visit(func_node)

    def visit_Lambda(self, node: ast.Lambda):
        scope = self.pull_scope(node, include_as_variable=False)
        if node not in self.node_to_corresponding_scope:
            self.node_to_corresponding_scope[node] = FunctionScope(node, scope)
        scope.add_function(
            node, self.node_to_corresponding_scope[node], include_as_variable=False
        )
        super().generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        scope = self.pull_scope(node)
        scope.add_exception(node)
        super().generic_visit(node)

    def visit_comprehension_generic(
        self,
        targets: list[ast.expr],
        comprehensions: list[ast.comprehension],
        node: ast.AST,
    ):
        # mate sure to visit the comprehensions first
        visit_all(self, comprehensions)
        visit_all(self, targets)

    def visit_comprehension(self, node: ast.comprehension):
        scope = self.pull_scope(node, include_as_variable=False)
        if node not in self.node_to_corresponding_scope:
            self.node_to_corresponding_scope[node] = FunctionScope(node, scope)
        scope.add_function(
            node, self.node_to_corresponding_scope[node], include_as_variable=False
        )
        super().generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        scope = self.pull_scope(node)
        if node not in self.node_to_corresponding_scope:
            self.node_to_corresponding_scope[node] = ClassScope(node, scope)
        class_scope_fields, parent_scope_fields = compute_class_fields(node)
        visit_all(self, *parent_scope_fields)
        scope.add_class(node, self.node_to_corresponding_scope[node])
        visit_all(self, *class_scope_fields)

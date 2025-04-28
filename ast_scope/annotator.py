from __future__ import annotations

import abc
import ast
from typing import Iterable

from typing_extensions import Self

from .group_similar_constructs import GroupSimilarConstructsVisitor
from .utils import compute_class_fields, name_of_alias


class IntermediateScope(abc.ABC):
    """
    Represents a scope for the purposes of the annotator object. This isn't actually a scope but something from which
        scope can be deduced.
    """

    def __init__(self):
        self.referenced_variables: set[str] = set()
        self.written_variables: set[str] = set()
        self.nonlocal_variables: set[str] = set()
        self.global_variables: set[str] = set()

    def load(self, variable: str):
        self.referenced_variables.add(variable)

    def modify(self, variable: str):
        self.written_variables.add(variable)

    def globalize(self, variable: str):
        self.global_variables.add(variable)

    def nonlocalize(self, variable: str):
        self.nonlocal_variables.add(variable)

    @abc.abstractmethod
    def global_frame(self) -> "IntermediateGlobalScope":
        pass

    @abc.abstractmethod
    def find(
        self, name: str, is_assignment: bool, global_acceptable: bool = True
    ) -> Self | None:
        """
        Finds the actual frame containing the variable name, or None if no frame exists
        """


class IntermediateGlobalScope(IntermediateScope):
    def find(self, name: str, is_assignment: bool, global_acceptable: bool = True):
        if not global_acceptable:
            return None
        return self

    def global_frame(self):
        return self


class IntermediateScopeWithParent(IntermediateScope):
    def __init__(self, parent: IntermediateScope):
        self.parent = parent
        super().__init__()

    def true_parent(self) -> IntermediateScope:
        parent = self.parent
        while isinstance(parent, IntermediateClassScope):
            parent = parent.parent
        return parent


class IntermediateFunctionScope(IntermediateScopeWithParent):
    def __init__(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.comprehension | ast.Lambda,
        parent: IntermediateScope,
    ):
        super().__init__(parent)
        self.node = node

    def global_frame(self) -> IntermediateGlobalScope:
        return self.true_parent().global_frame()

    def find(self, name: str, is_assignment: bool, global_acceptable: bool = True):
        if name in self.global_variables:
            return self.global_frame()
        if name in self.nonlocal_variables:
            return self.true_parent().find(name, is_assignment, global_acceptable=False)
        if name in self.written_variables:
            return self
        return self.true_parent().find(name, is_assignment, global_acceptable)


class IntermediateClassScope(IntermediateScopeWithParent):
    def __init__(
        self, node: ast.ClassDef, parent: IntermediateScope, class_binds_near: bool
    ):
        super().__init__(parent)
        self.node = node
        self.class_binds_near = class_binds_near

    def global_frame(self) -> IntermediateGlobalScope:
        return self.true_parent().global_frame()

    def find(self, name: str, is_assignment: bool, global_acceptable: bool = True):
        if self.class_binds_near:
            # anything can be in a class frame
            return self
        if is_assignment:
            return self
        return self.parent.find(name, is_assignment, global_acceptable)


class GrabVariable(ast.NodeVisitor):
    """
    Dumps variables from a given name object into the given scope.
    """

    def __init__(
        self,
        scope: IntermediateScope,
        variable: ast.Name,
        annotation_dict: dict[ast.AST, tuple[str, IntermediateScope, bool]],
    ):
        self.scope = scope
        self.variable = variable
        self.annotation_dict = annotation_dict

    def visit_generic(self, node: ast.AST):
        raise RuntimeError(f"Unsupported node type: {node}")

    def load(self):
        self.annotation_dict[self.variable] = self.variable.id, self.scope, False
        self.scope.load(self.variable.id)

    def modify(self):
        self.annotation_dict[self.variable] = self.variable.id, self.scope, True
        self.scope.modify(self.variable.id)

    def visit_Load(self, node: ast.Load):
        del node
        self.load()

    def visit_Store(self, node: ast.Store):
        del node
        self.modify()

    def visit_Del(self, node: ast.Del):
        del node
        self.modify()

    def visit_AugLoad(self, node: ast.AugLoad):
        raise RuntimeError("Unsupported: AugStore")

    def visit_AugStore(self, node: ast.AugStore):
        raise RuntimeError("Unsupported: AugStore")


class ProcessArguments(ast.NodeVisitor):
    def __init__(self, expr_scope: "AnnotateScope", arg_scope: "AnnotateScope"):
        self.expr_scope = expr_scope
        self.arg_scope = arg_scope

    def visit_arg(self, node: ast.arg):
        self.arg_scope.visit(node)
        visit_all(self.expr_scope, node.annotation, getattr(node, "type_comment", None))

    def visit_arguments(self, node: ast.AST):
        super().generic_visit(node)

    def generic_visit(self, node: ast.AST):
        self.expr_scope.visit(node)


class AnnotateScope(GroupSimilarConstructsVisitor):
    def __init__(
        self,
        scope: IntermediateScope,
        annotation_dict: dict[ast.AST, tuple[str, IntermediateScope, bool]],
        class_binds_near: bool,
    ):
        self.scope = scope
        self.annotation_dict = annotation_dict
        self.class_binds_near = class_binds_near

    def annotate_intermediate_scope(self, node: ast.AST, name: str, is_assign: bool):
        self.annotation_dict[node] = name, self.scope, is_assign

    def visit_Name(self, node: ast.Name):
        GrabVariable(self.scope, node, self.annotation_dict).generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        assert node.name
        self.annotate_intermediate_scope(node, node.name, True)
        self.scope.modify(node.name)
        visit_all(self, node.type, node.body)

    def visit_alias(self, node: ast.alias):
        variable = name_of_alias(node)
        self.annotate_intermediate_scope(node, variable, True)
        self.scope.modify(variable)

    def visit_arg(self, node: ast.arg):
        self.annotate_intermediate_scope(node, node.arg, True)
        self.scope.modify(node.arg)

    def create_subannotator(self, scope: IntermediateScope):
        return AnnotateScope(scope, self.annotation_dict, self.class_binds_near)

    def visit_function_def(
        self, func_node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool
    ):
        del is_async
        self.annotate_intermediate_scope(func_node, func_node.name, True)
        self.scope.modify(func_node.name)
        subscope = self.create_subannotator(
            IntermediateFunctionScope(func_node, self.scope)
        )
        visit_all(
            self, getattr(func_node, "type_comment", None), func_node.decorator_list
        )
        ProcessArguments(self, subscope).visit(func_node.args)
        visit_all(subscope, func_node.body, func_node.returns)

    def visit_Lambda(self, node: ast.Lambda):
        self.annotate_intermediate_scope(node, "<lambda>", False)
        subscope = self.create_subannotator(IntermediateFunctionScope(node, self.scope))
        ProcessArguments(self, subscope).visit(node.args)
        visit_all(subscope, node.body)

    def visit_comprehension_generic(
        self,
        targets: list[ast.expr],
        comprehensions: list[ast.comprehension],
        node: ast.AST,
    ):
        del node
        current_scope = self
        for comprehension in comprehensions:
            self.annotate_intermediate_scope(comprehension, "<comp>", False)
            subscope = self.create_subannotator(
                IntermediateFunctionScope(comprehension, current_scope.scope)
            )
            visit_all(current_scope, comprehension.iter)
            visit_all(subscope, comprehension.target, comprehension.ifs)
            current_scope = subscope
        visit_all(current_scope, targets)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.annotate_intermediate_scope(node, node.name, True)
        self.scope.modify(node.name)
        subscope = self.create_subannotator(
            IntermediateClassScope(node, self.scope, self.class_binds_near)
        )
        class_scope_fields, parent_scope_fields = compute_class_fields(node)
        visit_all(subscope, *class_scope_fields)
        visit_all(self, *parent_scope_fields)

    def visit_Global(self, node: ast.Global):
        for name in node.names:
            self.scope.globalize(name)

    def visit_Nonlocal(self, node: ast.Nonlocal):
        for name in node.names:
            self.scope.nonlocalize(name)


def visit_all(visitor: ast.NodeVisitor, *nodes: Iterable[ast.AST] | ast.AST | None):
    for node in nodes:
        if node is None:
            pass
        elif isinstance(node, Iterable):
            visit_all(visitor, *node)
        else:
            visitor.visit(node)

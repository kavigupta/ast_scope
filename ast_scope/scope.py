from __future__ import annotations

import abc
import ast

import attr
from typing_extensions import Self

from .annotator import name_of_alias


@attr.s
class Variables:
    arguments: set[ast.arg] = attr.ib(factory=set)
    variables: set[ast.Name] = attr.ib(factory=set)
    functions: set[
        ast.FunctionDef | ast.Lambda | ast.comprehension | ast.AsyncFunctionDef
    ] = attr.ib(factory=set)
    classes: set[ast.ClassDef] = attr.ib(factory=set)
    import_statements: set[ast.alias] = attr.ib(factory=set)
    exceptions: set[ast.ExceptHandler] = attr.ib(factory=set)

    @property
    def node_to_symbol(self):
        result: dict[ast.AST, str] = {}
        result.update({var: var.arg for var in self.arguments})
        result.update({var: var.id for var in self.variables})
        result.update(
            {
                var: var.name
                for var in self.functions
                if isinstance(var, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
        )
        result.update({var: var.name for var in self.classes})
        result.update({var: name_of_alias(var) for var in self.import_statements})
        result.update({var: var.name for var in self.exceptions if var.name})
        return result

    @property
    def all_symbols(self):
        return set(self.node_to_symbol.values())


class Scope(abc.ABC):
    def __init__(self):
        self.variables = Variables()

    def add_argument(self, node: ast.arg):
        self.variables.arguments.add(node)

    def add_variable(self, node: ast.Name):
        self.variables.variables.add(node)

    def add_import(self, node: ast.alias):
        self.variables.import_statements.add(node)

    def add_exception(self, node: ast.ExceptHandler):
        self.variables.exceptions.add(node)

    @abc.abstractmethod
    def add_child(self, scope: Self):
        pass

    def add_function(
        self,
        node: ast.FunctionDef | ast.Lambda | ast.comprehension | ast.AsyncFunctionDef,
        function_scope: Self,
        include_as_variable: bool,
    ):
        if include_as_variable:
            self.variables.functions.add(node)
        self.add_child(function_scope)

    def add_class(self, node: ast.ClassDef, class_scope: Self):
        self.variables.classes.add(node)
        self.add_child(class_scope)

    @property
    def symbols_in_frame(self):
        return self.variables.all_symbols


class ScopeWithChildren(Scope):
    def __init__(self):
        Scope.__init__(self)
        self.children: list[Scope] = []

    def add_child(self, scope: Scope):
        self.children.append(scope)


class ScopeWithParent(Scope, abc.ABC):
    def __init__(self, parent: Scope):
        super().__init__()
        self.parent = parent


class ErrorScope(Scope):
    def add_child(self, scope):
        raise RuntimeError("Error Scope cannot have children")


class GlobalScope(ScopeWithChildren):
    pass


class FunctionScope(ScopeWithChildren, ScopeWithParent):
    def __init__(
        self,
        function_node: (
            ast.FunctionDef | ast.Lambda | ast.comprehension | ast.AsyncFunctionDef
        ),
        parent: Scope,
    ):
        ScopeWithChildren.__init__(self)
        ScopeWithParent.__init__(self, parent)
        self.function_node = function_node


class ClassScope(ScopeWithParent):
    def __init__(self, class_node: ast.ClassDef, parent: Scope):
        super().__init__(parent)
        self.class_node = class_node

    def add_child(self, scope):
        return self.parent.add_child(scope)

import abc

import attr

from .annotator import name_of_alias


@attr.s
class Variables:
    arguments = attr.ib(attr.Factory(set))
    variables = attr.ib(attr.Factory(set))
    functions = attr.ib(attr.Factory(set))
    classes = attr.ib(attr.Factory(set))
    import_statements = attr.ib(attr.Factory(set))
    exceptions = attr.ib(attr.Factory(set))

    @property
    def node_to_symbol(self):
        result = {}
        result.update({var: var.arg for var in self.arguments})
        result.update({var: var.id for var in self.variables})
        result.update({var: var.name for var in self.functions | self.classes})
        result.update({var: name_of_alias(var) for var in self.import_statements})
        result.update({var: var.name for var in self.exceptions})
        return result

    @property
    def all_symbols(self):
        return set(self.node_to_symbol.values())


class Scope(abc.ABC):
    def __init__(self):
        self.variables = Variables()

    def add_argument(self, node):
        self.variables.arguments.add(node)

    def add_variable(self, node):
        self.variables.variables.add(node)

    def add_import(self, node):
        self.variables.import_statements.add(node)

    def add_exception(self, node):
        self.variables.exceptions.add(node)

    @abc.abstractmethod
    def add_child(self, scope):
        pass

    def add_function(self, node, function_scope, include_as_variable):
        if include_as_variable:
            self.variables.functions.add(node)
        self.add_child(function_scope)

    def add_class(self, node, class_scope):
        self.variables.classes.add(node)
        self.add_child(class_scope)

    @property
    def symbols_in_frame(self):
        return self.variables.all_symbols


class ScopeWithChildren(Scope):
    def __init__(self):
        Scope.__init__(self)
        self.children = []

    def add_child(self, scope):
        self.children.append(scope)


class ScopeWithParent(Scope, abc.ABC):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent


class ErrorScope(Scope):
    def add_child(self, scope):
        raise RuntimeError("Error Scope cannot have children")


class GlobalScope(ScopeWithChildren):
    pass


class FunctionScope(ScopeWithChildren, ScopeWithParent):
    def __init__(self, function_node, parent):
        ScopeWithChildren.__init__(self)
        ScopeWithParent.__init__(self, parent)
        self.function_node = function_node


class ClassScope(ScopeWithParent):
    def __init__(self, class_node, parent):
        super().__init__(parent)
        self.class_node = class_node

    def add_child(self, scope):
        return self.parent.add_child(scope)

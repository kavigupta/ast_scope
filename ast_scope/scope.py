import attr
import abc

@attr.s
class Variables:
    variables = attr.ib(attr.Factory(set))
    functions = attr.ib(attr.Factory(set))
    classes = attr.ib(attr.Factory(set))
    import_statements = attr.ib(attr.Factory(set))

class Scope(abc.ABC):
    def __init__(self):
        self.variables = Variables()
    def add_variable(self, node):
        self.variables.variables.add(node)
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


class ScopeWithChildren(Scope):
    def __init__(self):
        Scope.__init__(self)
        self.children = []
    def add_child(self, scope):
        self.children.append(scope)

class ScopeWithParent(Scope):
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

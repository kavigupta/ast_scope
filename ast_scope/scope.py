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
    def add_child(self, scope):
        self.children.append(scope)
    def add_function(self, node, function_scope, include_as_variable):
        if include_as_variable:
            self.variables.functions.add(node)
        self.add_child(function_scope)
    def add_class(self, node, class_scope):
        self.variables.classes.add(node)
        self.add_child(class_scope)


class ErrorScope(Scope):
    pass

class ScopeWithChildren(Scope, abc.ABC):
    def __init__(self):
        super().__init__()
        self.children = []

class GlobalScope(ScopeWithChildren):
    pass

class FunctionScope(ScopeWithChildren):
    def __init__(self, function_node):
        super().__init__()
        self.function_node = function_node

class ClassScope(Scope):
    def __init__(self, class_node):
        super().__init__()
        self.class_node = class_node

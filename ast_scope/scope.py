import attr
import abc

@attr.s
class Variables:
    variables = attr.ib(default=set())
    functions = attr.ib(default=set())
    classes = attr.ib(default=set())
    import_statements = attr.ib(default=set())

class Scope(abc.ABC):
    def add_variable(self, node):
        self.variables.variables.add(node)
    def add_function(self, node, function_scope):
        self.variables.functions.add(node)
        self.children.append(function_scope)
    def add_class(self, node, class_scope):
        self.variables.classes.add(node)
        self.children.append(class_scope)


@attr.s
class ErrorScope(Scope):
    variables = attr.ib(default=Variables())

@attr.s
class GlobalScope(Scope):
    variables = attr.ib(default=Variables())
    children = attr.ib(default=list())

@attr.s
class FunctionScope(Scope):
    function_node = attr.ib()
    variables = attr.ib(default=Variables())
    children = attr.ib(default=list())

@attr.s
class ClassScope(Scope):
    class_node = attr.ib()
    variables = attr.ib(default=Variables())

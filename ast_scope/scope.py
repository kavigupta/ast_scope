import attr
import abc

@attr.s
class Variables:
    variables = attr.ib(attr.Factory(set))
    functions = attr.ib(attr.Factory(set))
    classes = attr.ib(attr.Factory(set))
    import_statements = attr.ib(attr.Factory(set))

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
    variables = attr.ib(attr.Factory(Variables))

@attr.s
class GlobalScope(Scope):
    variables = attr.ib(attr.Factory(Variables))
    children = attr.ib(attr.Factory(list))

@attr.s
class FunctionScope(Scope):
    function_node = attr.ib()
    variables = attr.ib(attr.Factory(Variables))
    children = attr.ib(attr.Factory(list))

@attr.s
class ClassScope(Scope):
    class_node = attr.ib()
    variables = attr.ib(attr.Factory(Variables))

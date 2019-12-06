
import ast
import abc

class IntermediateScope(abc.ABC):
    """
    Represents a scope for the purposes of the annotator object. This isn't actually a scope but something from which
        scope can be deduced.
    """
    def __init__(self):
        self.referenced_variables = set()
        self.written_variables = set()
        self.nonlocal_variables = set()
        self.global_variables = set()

    def load(self, variable):
        self.referenced_variables.add(variable)

    def modify(self, variable):
        self.written_variables.add(variable)

    def globalize(self, variable):
        self.global_variables.add(variable)

    def nonlocalize(self, variable):
        self.nonlocal_variables.add(variable)

    @abc.abstractmethod
    def global_frame(self):
        pass

    @abc.abstractmethod
    def find(self, name, global_acceptable=True):
        """
        Finds the actual frame containing the variable name, or None if no frame exists
        """
        pass

    def true_parent(self):
        parent = self.parent
        while isinstance(parent, IntermediateClassScope):
            parent = parent.parent
        return parent

class IntermediateGlobalScope(IntermediateScope):
    def find(self, name, global_acceptable=True):
        if not global_acceptable:
            return None
        return self

    def global_frame(self):
        return self

class IntermediateFunctionScope(IntermediateScope):
    def __init__(self, node, parent):
        super().__init__()
        self.node = node
        self.parent = parent

    def global_frame(self):
        return self.true_parent().global_frame()

    def find(self, name, global_acceptable=True):
        if name in self.global_variables:
            return self.global_frame()
        if name in self.nonlocal_variables:
            return self.true_parent().find(name, global_acceptable=False)
        if name in self.written_variables:
            return self
        return self.true_parent().find(name, global_acceptable)


class IntermediateClassScope(IntermediateScope):
    def __init__(self, node, parent):
        super().__init__()
        self.node = node
        self.parent = parent
    def global_frame(self):
        return self.true_parent().find(self)

class GrabVariable(ast.NodeVisitor):
    """
    Dumps variables from a given name object into the given scope.
    """
    def __init__(self, scope, variable):
        self.scope = scope
        self.variable = variable

    def visit_generic(self, node):
        raise RuntimeError("Unsupported node type: {node}".format(node=node))

    def visit_Name(self, node):
        super().visit_generic(node)

    def visit_Load(self, _):
        self.scope.load(self.variable)

    def visit_Store(self, _):
        self.scope.modify(self.variable)

    def visit_Del(self, _):
        self.scope.modify(self.variable)

    def visit_AugLoad(self, _):
        raise RuntimeError("Unsupported: AugStore")

    def visit_AugStore(self, _):
        raise RuntimeError("Unsupported: AugStore")

    def visit_Param(self, _):
        self.scope.store(self.variable)

class AnnotateScope(ast.NodeVisitor):
    def __init__(self, scope, annotation_dict):
        self.scope = scope
        self.annotation_dict = annotation_dict

    def annotate_intermediate_scope(self, node, name):
        self.annotation_dict[node] = name, self.scope

    def visit_Name(self, name_node):
        self.annotate_intermediate_scope(name_node, name_node.id)
        GrabVariable(self.scope, name_node.id).generic_visit(name_node)

    def visit_alias(self, alias_node):
        if alias_node.asname is not None:
            variable = alias_node.asname
        else:
            variable = alias_node.name
        self.annotate_intermediate_scope(alias_node, variable)
        self.scope.modify(variable)

    def visit_arg(self, arg):
        self.annotate_intermediate_scope(arg, arg.arg)
        self.scope.modify(arg.arg)

    def visit_FunctionDef(self, func_node):
        self.annotate_intermediate_scope(func_node, func_node.name)
        self.scope.modify(func_node.name)
        subscope = AnnotateScope(IntermediateFunctionScope(func_node, self.scope), self.annotation_dict)
        ast.NodeVisitor.generic_visit(subscope, func_node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, class_node):
        self.annotate_intermediate_scope(class_node, class_node.name)
        self.scope.modify(class_node.name)
        subscope = AnnotateScope(IntermediateClassScope(class_node, self.scope), self.annotation_dict)
        ast.NodeVisitor.generic_visit(subscope, class_node)

    def visit_Global(self, global_node):
        for name in global_node.names:
            self.scope.globalize(name)

    def visit_Nonlocal(self, nonlocal_node):
        for name in nonlocal_node.names:
            self.scope.nonlocalize(name)

from __future__ import annotations

import ast


class GroupSimilarConstructsVisitor(ast.NodeVisitor):
    def visit_function_def(
        self, func_node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool
    ):
        del is_async
        return self.generic_visit(func_node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        return self.visit_function_def(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        return self.visit_function_def(node, is_async=True)

    def visit_comprehension_generic(
        self,
        targets: list[ast.expr],
        comprehensions: list[ast.comprehension],
        node: ast.AST,
    ):
        del targets, comprehensions
        return self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp):
        return self.visit_comprehension_generic(
            [node.key, node.value], node.generators, node
        )

    def visit_ListComp(self, node: ast.ListComp):
        return self.visit_comprehension_generic([node.elt], node.generators, node)

    def visit_SetComp(self, node: ast.SetComp):
        return self.visit_comprehension_generic([node.elt], node.generators, node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        return self.visit_comprehension_generic([node.elt], node.generators, node)

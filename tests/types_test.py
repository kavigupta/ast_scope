import ast

import ast_scope
from .utils import DisplayAnnotatedTestCase, remove_directives


class TypeAnnotationTest(DisplayAnnotatedTestCase):
    def test_basic_assignment(self):
        annotated_code = """
        @{g}f{<3.8!g}
        {>=3.8!g}class A:
            pass

        {g}class B({g}A, x={g}A):
            pass

        {g}C = {g}B
        {g}CONSTANT: {g}C = {g}C()
        {g}CONST: {g}C
        """
        self.assertAnnotationWorks(annotated_code)
        scope_info = ast_scope.annotate(ast.parse(remove_directives(annotated_code)))

        self.assertEqual(
            scope_info.static_dependency_graph._DiGraph__adjacency_list,
            {
                "B": set(),
                "C": set(),
                "CONSTANT": set(),
                "CONST": set(),
                "A": set(),
                "f": set(),
            },
        )

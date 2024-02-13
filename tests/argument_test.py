
from .utils import DisplayAnnotatedTestCase, from_version

class DifferentArgumentTypes(DisplayAnnotatedTestCase):
    def test_multiple_arguments(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x, {~f@1:0}y):
                pass
            """
        )
    def test_keyword_only_arguments(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x, *, {~f@1:0}y, {~f@1:0}z):
                pass
            """
        )
    @from_version(3, 8)
    def test_positional_only_arguments(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x, /, {~f@1:0}y, {~f@1:0}z):
                pass
            """
        )
    def test_keyword_arguments(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x, *, {~f@1:0}y=2, {~f@1:0}z):
                pass
            """
        )
    def test_star_args(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x, *{~f@1:0}args, {~f@1:0}y=2, {~f@1:0}z):
                pass
            """
        )
    def test_starstar_kwargs(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x, **{~f@1:0}kwargs):
                pass
            """
        )


class DefaultArguments(DisplayAnnotatedTestCase):
    def test_default_arguments(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x={g}x):
                pass
            """
        )
    def test_complex_expression_default(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x={g}f({g}x)):
                pass
            """
        )
    def test_type(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x={g}List[{g}int]):
                pass
            """
        )
    def test_typing(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x : {g}x={g}List[{g}int]) -> {g}int:
                pass
            """
        )
    def test_inherits_proper_parent(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x):
                {~f@1:0}def g({~g@2:4}x={~f@1:0}x):
                    pass
            """
        )

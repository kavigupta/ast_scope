from .utils import DisplayAnnotatedTestCase


class ExceptionTests(DisplayAnnotatedTestCase):
    def test_multiple_arguments(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                try:
                    pass
                {~f@1:0}except {g}Exception as e:
                    pass
            """
        )

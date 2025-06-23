from .utils import DisplayAnnotatedTestCase


class ExceptionTests(DisplayAnnotatedTestCase):

    def test_basic_named(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                try:
                    {~f@1:0}z = 1
                {~f@1:0}except {g}Exception as e:
                    {~f@1:0}x = {~f@1:0}e
                finally:
                    {~f@1:0}y = 1
            """
        )

    def test_no_name(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                try:
                    {~f@1:0}z = 1
                except {g}Exception:
                    {~f@1:0}x = 1
            """
        )

    def test_multiple_exceptions(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                try:
                    {~f@1:0}z = 1
                {~f@1:0}except {g}Exception as e:
                    {~f@1:0}x = {~f@1:0}e
                {~f@1:0}except {g}ValueError as e2:
                    {~f@1:0}y = {~f@1:0}e2
            """
        )

from .utils import DisplayAnnotatedTestCase

class FunctionFrameTest(DisplayAnnotatedTestCase):
    def test_basic_lambda(self):
        self.assertAnnotationWorks(
            """
            lambda {~@1:0}x: {~@1:0}x
            """
        )
    def test_noarg_lambda(self):
        self.assertAnnotationWorks(
            """
            lambda: {g}x
            """
        )
    def test_multiarg_lambda(self):
        self.assertAnnotationWorks(
            """
            lambda {~@1:0}x, {~@1:0}y, *{~@1:0}args: {~@1:0}x if {~@1:0}y else {~@1:0}args
            """
        )
    def test_nested_lambdas(self):
        self.assertAnnotationWorks(
            """
            lambda {~@1:0}x, {~@1:0}y: lambda {~@1:13}y, {~@1:13}z: {g}t + {~@1:0}x + {~@1:13}y + {~@1:13}z
            {g}t = {g}x = {g}y = {g}z = 0
            """
        )
    def test_default_params_in_parent(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x):
                lambda {~@2:4}x={~f@1:0}x: {~@2:4}x
            """
        )

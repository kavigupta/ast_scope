from .utils import DisplayAnnotatedTestCase

class ClassTests(DisplayAnnotatedTestCase):
    def test_class(self):
        self.assertAnnotationWorks(
            """
            {g}class X: pass
            """
        )
    def test_variables_in_frame(self):
        self.assertAnnotationWorks(
            """
            {g}class X:
                {-X@1:0}x = 2
                {-X@1:0}y
                {-X@1:0}y = {-X@1:0}x
            """
        )
    def test_function(self):
        self.assertAnnotationWorks(
            """
            {g}class X:
                {-X@1:0}def f(): pass
            """
        )
    def test_parent_is_global(self):
        self.assertAnnotationWorks(
            """
            {g}class X:
                {-X@1:0}x = 2
                {-X@1:0}def f():
                    return {g}x
            """
        )
    def test_parent_is_local(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x):
                {~f@1:0}class X:
                    {-X@2:4}x = 2
                    {-X@2:4}def f():
                        return {~f@1:0}x
            """
        )
    def test_nested_class_frames(self):
        self.assertAnnotationWorks(
            """
            {g}class Y:
                {-Y@1:0}class X:
                    {-X@2:4}x = 2
                    {-X@2:4}def f():
                        return {g}x
            """
        )
    def test_nonlocal_class_frames(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x):
                {~f@1:0}class X:
                    {-X@2:4}x = 2
                    {-X@2:4}def f():
                        nonlocal x
                        {~f@1:0}x = 2
                        return {~f@1:0}x
            """
        )
    def test_default_method_argument(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x):
                {~f@1:0}class X:
                    {-X@2:4}x = 2
                    {-X@2:4}def f({~f@4:8}x={-X@2:4}x):
                        pass
            """
        )
    def test_listcomp_value(self):
        self.assertAnnotationWorks(
            """
            {g}class X:
                {-X@1:0}x = 2
                [{g}x for {~@3:11}t in {-X@1:0}x]
            """
        )

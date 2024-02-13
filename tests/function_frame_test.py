from .utils import DisplayAnnotatedTestCase, from_version, pre_version

class FunctionFrameTest(DisplayAnnotatedTestCase):
    def test_no_parameter_function(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                {~f@1:0}x = 2
                {~f@1:0}y = 3
            """
        )
    def test_global_statement(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                global x, y
                {g}x = 2
                {g}y = 3
                {~f@1:0}z = 4
            """
        )
    def test_inherits(self):
        self.assertAnnotationWorks(
            """
            {g}x = {g}y = 2
            {g}def f():
                {~f@2:0}x = {~f@2:0}z = 3
                return {~f@2:0}x + {g}y
            """
        )
    def test_self_reference(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                {~f@1:0}x = 7
                return {g}f, {~f@1:0}x
            """
        )
    def test_parameters(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x, {~f@1:0}y=2, *, {~f@1:0}z):
                pass
            """
        )
    @from_version(3, 7)
    def test_async_parameters_new(self):
        self.assertAnnotationWorks(
            """
            {g}async def f({~f@1:0}x, {~f@1:0}y=2, *, {~f@1:0}z):
                pass
            """
        )
    @pre_version(3, 7)
    def test_async_parameters_old(self):
        self.assertAnnotationWorks(
            """
            async {g}def f({~f@1:6}x, {~f@1:6}y=2, *, {~f@1:6}z):
                pass
            """
        )
    def test_nested_function(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x, {~f@1:0}y):
                {~f@1:0}def g({~g@2:4}y, {~g@2:4}z):
                    return {g}t + {~f@1:0}x + {~g@2:4}y + {~g@2:4}z
            {g}t = {g}x = {g}y = {g}z = 1
            """
        )
    def test_set_after_get(self):
        self.assertAnnotationWorks(
            """
            {g}x = 1
            {g}def f():
                {~f@2:0}x
                {~f@2:0}x = 2
            """
        )
    def test_not_found_to_be_global(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                {g}x
            """
        )
    @pre_version(3, 8)
    def test_decorator_top_level_old(self):
        self.assertAnnotationWorks(
            """
            {g}@{g}x
            def f({~f@1:0}x):
                {~f@1:0}@{~f@1:0}x
                def g({~g@3:4}x):
                    pass
            """
        )
    @from_version(3, 8)
    def test_decorator_top_level_new(self):
        self.assertAnnotationWorks(
            """
            @{g}x
            {g}def f({~f@2:0}x):
                @{~f@2:0}x
                {~f@2:0}def g({~g@4:4}x):
                    pass
            """
        )
    def test_def_is_assign(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                {~f@1:0}def g(): pass
                return {~f@1:0}g
            {g}def g(): pass
            """
        )

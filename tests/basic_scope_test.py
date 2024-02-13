
from .utils import DisplayAnnotatedTestCase

class GlobalFrameTest(DisplayAnnotatedTestCase):
    def test_global_var(self):
        self.assertAnnotationWorks("{g}x = 2")
    def test_global_augassign(self):
        self.assertAnnotationWorks("{g}x += 2")
    def test_multiline_global(self):
        self.assertAnnotationWorks(
            "{g}x = 1\n{g}y = 2"
        )
    def test_lookups(self):
        self.assertAnnotationWorks(
            "{g}x = 1\n{g}y = {g}x"
        )
    def test_function(self):
        self.assertAnnotationWorks(
            "{g}def f(): pass"
        )

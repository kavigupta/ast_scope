
from .utils import DisplayAnnotatedTestCase

class SpecialSymbolsTest(DisplayAnnotatedTestCase):
    def test_booleans(self):
        self.assertAnnotationWorks(
            """
            {g}x = True, False, None
            """
        )

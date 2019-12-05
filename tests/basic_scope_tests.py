
import unittest

from .utils import classify_all

class GlobalFrameTest(unittest.TestCase):
    def test_global_var(self):
        self.assertEqual(
            classify_all("x = 2"),
            {
                'x@1:0' : 'global',
            }
        )
    def test_global_augassign(self):
        self.assertEqual(
            classify_all("x += 2"),
            {
                'x@1:0' : 'global',
            }
        )
    def test_multiline_global(self):
        self.assertEqual(
            classify_all("x = 1\ny = 2"),
            {
                'x@1:0' : 'global',
                'y@2:0' : 'global',
            }
        )
    def test_function(self):
        self.assertEqual(
            classify_all("def f(): pass"),
            {
                'f@1:0' : 'global',
            }
        )


no_parameter_function = """
def f():
    x = 2
    y = 3
""".strip()

function_with_globals = """
def f():
    global x, y
    x = 2
    y = 3
    z = 4
""".strip()

class FunctionFrameTest(unittest.TestCase):
    def test_no_parameter_function(self):
        self.assertEqual(
            classify_all(function_with_globals),
            {
                'f@1:0' : 'global',
                'x@3:4' : 'global',
                'y@4:4' : 'global',
                'z@5:4' : 'function[f@1:0]',
            }
        )

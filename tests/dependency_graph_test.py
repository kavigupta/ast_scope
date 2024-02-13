from .utils import DisplayAnnotatedTestCase

class TestClassDefault(DisplayAnnotatedTestCase):
    def testEmptyGraph(self):
        self.assertGraphWorks(
            """
            2 + 10
            """,
            vertices=[],
            edges=[]
        )
    def testJustVariables(self):
        self.assertGraphWorks(
            """
            x + y
            a, b = c, x
            """,
            vertices=["x", "y", "a", "b", "c"],
            edges=[]
        )
    def testFunctionWithNoGlobals(self):
        self.assertGraphWorks(
            """
            def f(x):
                return x ** x
            """,
            vertices=["f"],
            edges=[]
        )
    def testRecursiveFunction(self):
        self.assertGraphWorks(
            """
            def f(x):
                return f(x)
            """,
            vertices=["f"],
            edges=[("f", "f")]
        )
    def testGraphDirection(self):
        self.assertGraphWorks(
            """
            def f(x):
                return g(x) ** 2
            def g(x):
                return x ** 2
            """,
            vertices=["f", "g"],
            edges=[("f", "g")]
        )
    def testRefersToVariables(self):
        self.assertGraphWorks(
            """
            def f(x):
                return g(x) ** 2 + y
            def g(y):
                return x ** 2 + y
            """,
            vertices=["f", "g", "x", "y"],
            edges=[("f", "g"), ("f", "y"), ("g", "x")]
        )
    def testRefersToImportStatements(self):
        self.assertGraphWorks(
            """
            def f(x):
                global os
                import os
            """,
            vertices=["f", "os"],
            edges=[("f", "os")]
        )
    def testLocalFunctionsDontGetNodes(self):
        self.assertGraphWorks(
            """
            def f(x):
                def g(y):
                    pass
            """,
            vertices=["f"],
            edges=[]
        )
    def testReferencesToClasses(self):
        self.assertGraphWorks(
            """
            class X:
                def f(x):
                    return h(x)
            def g(x):
                return X.f(3)
            def h(x):
                return 2
            """,
            vertices=["X", "g", "h"],
            edges=[("X", "h"), ("g", "X")]
        )
    def testReferenceToImport(self):
        self.assertGraphWorks(
            """
            import os
            def g(x):
                return X.f(3)
            def h(x):
                return os.system("rm -r hi")
            """,
            vertices=["os", "g", "h", "X"],
            edges=[("g", "X"), ("h", "os")]
        )

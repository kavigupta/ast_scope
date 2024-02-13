from .utils import DisplayAnnotatedTestCase

class FunctionFrameTest(DisplayAnnotatedTestCase):
    def test_listcomp(self):
        self.assertAnnotationWorks(
            """
            [{~@1:7}x for {~@1:7}x in {g}x]
            """
        )
    def test_listcomp_with_if(self):
        self.assertAnnotationWorks(
            """
            [{~@1:7}x for {~@1:7}x in {g}x if {~@1:7}x + {g}y]
            """
        )
    def test_nested_listcomp(self):
        self.assertAnnotationWorks(
            """
            [[{~@1:8}x for {~@1:8}x in {~@2:11}x if {~@1:8}x]
                   for {~@2:11}x in {g}x if {~@2:11}x + {g}y]
            """
        )
    def test_serial_listcomp(self):
        self.assertAnnotationWorks(
            """
            [{~@4:11}x for {~@1:7}x in {g}x if {~@1:7}x
                   for {~@2:11}x in {~@1:7}x if {~@2:11}x + {g}y
                   for {~@3:11}x in {~@2:11}x if {~@3:11}x + {g}y
                   for {~@4:11}x in {~@3:11}x if {~@4:11}x + {g}y
            ]
            """
        )
    def test_serial_listcomp_with_if(self):
        self.assertAnnotationWorks(
            """
            [{~@3:8}z + {~@2:8}y + {g}x
                for {~@2:8}y in {g}x if {~@2:8}y + {g}x
                for {~@3:8}z in {~@2:8}y if {~@3:8}z + {~@2:8}y + {g}x
            ]
            """
        )
    def test_multi_if(self):
        self.assertAnnotationWorks(
            """
            [{~@2:8}y + {g}x
                for {~@2:8}y in {g}x if {~@2:8}y + {g}x if {~@2:8}y + {g}x
            ]
            """
        )
    def test_complex_target(self):
        self.assertAnnotationWorks(
            """
            [{~@2:8}x + {~@2:8}y
                for {~@2:8}x, {~@2:8}y in [{g}x, {g}y]
            ]
            """
        )
    def test_inherits_parent(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x, {~f@1:0}y):
                [{~@3:12}x + {~@3:12}y
                    for {~@3:12}x, {~@3:12}y in [{~f@1:0}x, {~f@1:0}y]
                ]
            """
        )
    def test_set_comprehension(self):
        self.assertAnnotationWorks("{{~@1:7}x for {~@1:7}x in 2}", "{x for x in 2}")
    def test_gen_comprehension(self):
        self.assertAnnotationWorks(
            """
            ({~@1:7}x for {~@1:7}x in 2)
            """
        )
    def test_dict_comprehension(self):
        self.assertAnnotationWorks("{{~@1:9}x:{~@1:9}y for {~@1:9}x, {~@1:9}y in 2}", "{x:y for x, y in 2}")

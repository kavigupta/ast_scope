from .utils import DisplayAnnotatedTestCase, from_version

class EqualityAssignmentTests(DisplayAnnotatedTestCase):
    def test_basic_assignment(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                {~f@1:0}x = 2
            """
        )
    def test_underscore(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                {~f@1:0}_ = 2
            """
        )
    def test_element_assignment(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                {g}x[0] = 2
            """
        )
    def test_aug_assignment(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                {~f@1:0}x += 2
            """
        )
    def test_multi_assignment(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                {~f@1:0}x, {~f@1:0}y = 1, 2
            """
        )
    @from_version(3, 8)
    def test_special_assigment(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                ({~f@1:0}x := 2)
            """
        )

class LoopAssignmentTests(DisplayAnnotatedTestCase):
    def test_basic_for_loop(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                for {~f@1:0}x in {g}range(2):
                    pass
            """
        )
    def test_multi_for_loop(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                for {~f@1:0}x, {~f@1:0}y in {g}range(2):
                    pass
            """
        )
    def test_itemizer_loop(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                for {~f@1:0}k, {g}d[{~f@1:0}k] in {g}range(2):
                    pass
            """
        )

class ImportAssignmentTests(DisplayAnnotatedTestCase):
    def test_global_import(self):
        self.assertAnnotationWorks(
            """
            import os
            {g}def f():
                {g}os
            """
        )
    def test_local_import(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                import os
                {~f@1:0}os
            """
        )
    def test_sub_import(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                from os import system
                {~f@1:0}system
                {g}os
            """
        )
    def test_star_import(self):
        self.assertAnnotationWorks(
            """
            from os import *
            """
        )
    def test_aliases(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                from os import system as a
                import sys as b
                {g}os
                {g}system
                {~f@1:0}a
                {g}sys
                {~f@1:0}b
            """
        )


from .utils import DisplayAnnotatedTestCase

class NonlocalTest(DisplayAnnotatedTestCase):
    def test_no_nonlocal(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x):
                {~f@1:0}def g():
                    {~g@2:4}x += 2
                return {~f@1:0}g
            """
        )
    def test_basic_nonlocal(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x):
                {~f@1:0}def g():
                    nonlocal x
                    {~f@1:0}x += 2
                return {~f@1:0}g
            """
        )
    def test_nonlocal_not_found(self):
        self.assertAnnotationWorks(
            """
            {g}def f():
                {~f@1:0}def g():
                    nonlocal x
                    {?}x += 2
                return {~f@1:0}g
            """
        )
    def test_nonlocal_found_in_most_recent_parent(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x):
                {~f@1:0}def g({~g@2:4}x):
                    {~g@2:4}def h():
                        nonlocal x
                        {~g@2:4}x += 2
                return {~f@1:0}g
            """
        )
    def test_nonlocal_found_in_parent_of_parent(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x):
                {~f@1:0}def g({~g@2:4}y):
                    {~g@2:4}def h():
                        nonlocal x
                        {~f@1:0}x += 2
                return {~f@1:0}g
            """
        )
    def test_global_escapes_scope(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x):
                {~f@1:0}def g({~g@2:4}y):
                    {~g@2:4}def h():
                        global x
                        {g}x += 2
                return {~f@1:0}g
            {g}x = 2
            """
        )
    def test_global_escapes_scope_even_without_declaration(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x):
                {~f@1:0}def g({~g@2:4}y):
                    {~g@2:4}def h():
                        global x
                        {g}x += 2
                return {~f@1:0}g
            """
        )
    def test_symbol_in_different_frame_from_parent(self):
        self.assertAnnotationWorks(
            """
            {g}def f({~f@1:0}x, {~f@1:0}y):
                {~f@1:0}def g({~g@2:4}y):
                    nonlocal x
                    {~f@1:0}def x():
                        {~g@2:4}y
            """
        )

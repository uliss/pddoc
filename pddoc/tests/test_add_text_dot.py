from unittest import TestCase
from ..pddocvisitor import add_text_dot, remove_text_dot


class TestAdd_text_dot(TestCase):
    def test_add_text_dot(self):
        self.assertEqual(add_text_dot(""), "")
        self.assertEqual(add_text_dot("."), ".")
        self.assertEqual(add_text_dot("test."), "test.")
        self.assertEqual(add_text_dot("test"), "test.")
        self.assertEqual(add_text_dot("test..."), "test...")
        self.assertEqual(add_text_dot("test  "), "test.")

    def remove_text_dot(self):
        self.assertEqual(remove_text_dot(""), "")
        self.assertEqual(remove_text_dot("."), "")
        self.assertEqual(remove_text_dot(".  "), "")
        self.assertEqual(remove_text_dot("test"), "test")
        self.assertEqual(remove_text_dot("test "), "test ")
        self.assertEqual(remove_text_dot("test."), "test")
        self.assertEqual(remove_text_dot("test.   "), "test")

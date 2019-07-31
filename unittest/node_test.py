import unittest

from mathlib.core.node import *


class NumNodeEqualTest(unittest.TestCase):
    def test_something(self):
        a = NumNode(4)
        b = NumNode(4)
        self.assertEqual(True, a == b)


class NumNodeDiffTest(unittest.TestCase):
    def test_something(self):
        a = NumNode(4)
        b = NumNode(-2)
        self.assertEqual(False, a == b)


class PolyNodeSimilarTest(unittest.TestCase):
    def test_something(self):
        x = VarNode('x')
        a = PolyNode(x, 3, 2)
        b = PolyNode(x, -7, 2)
        self.assertEqual(True, a.similar(b))


if __name__ == '__main__':
    unittest.main()

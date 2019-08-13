import unittest

from mathlib.utils.node_util import *


# class NumNodeEqualTest(unittest.TestCase):
#     def test(self):
#         a = NumNode(4)
#         b = NumNode(4)
#         self.assertEqual(True, a == b)
#
#
# class NumNodeDiffTest(unittest.TestCase):
#     def test(self):
#         a = NumNode(4)
#         b = NumNode(-2)
#         self.assertEqual(False, a == b)


class NumNodeSimilarTest(unittest.TestCase):
    def test(self):
        a = NumNode(4)
        b = NumNode(-2)
        self.assertEqual(True, a.similar(b))


class PolyNodeSimilarTest(unittest.TestCase):
    def test(self):
        x = VarNode('x')
        a = PolyNode(x, 2)
        b = PolyNode(x, 2)
        self.assertEqual(True, a.similar(b))


class FactorSimilarTest(unittest.TestCase):
    def test(self):
        x = VarNode('x')
        sin = TriNode('sin', VarNode('x'))
        ex = ExpoNode(math.e, VarNode('x'))
        a = FactorNode([x, sin], [ex, NumNode(2)])

        x = VarNode('x')
        sin = TriNode('sin', VarNode('x'))
        ex = ExpoNode(math.e, VarNode('x'))
        b = FactorNode([NumNode(10), x, sin], [ex])

        self.assertEqual(True, a.similar(b))


if __name__ == '__main__':
    unittest.main()

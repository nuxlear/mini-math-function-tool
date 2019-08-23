import unittest

from mathlib.tree.math_node import *
from mathlib.tree.atomic import *
from mathlib.tree.structural import *


class MathNodeBasicTest(unittest.TestCase):
    def num_init(self):
        n = NumNode(1)
        self.assertTrue(n.is_int(n.value))
        self.assertFalse(n.is_constant(n.value))

        self.assertEqual(repr(n), 'Num(1)')

    def var_init(self):
        n = VarNode('x')
        self.assertEqual(repr(n), 'Var(x)')


if __name__ == '__main__':
    unittest.main()

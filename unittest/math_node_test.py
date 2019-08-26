import unittest

from mathlib.tree.math_node import *


class MathNodeBasicTest(unittest.TestCase):
    def test_num_init(self):
        n = NumNode(1)
        self.assertTrue(n.is_int(n.value))
        self.assertFalse(n.is_constant(n.value))

        self.assertEqual('Num(1)', repr(n))
        self.assertEqual('1', str(n))

        m = NumNode('pi')
        self.assertEqual('pi', str(m))

    def test_var_init(self):
        n = VarNode('x')
        self.assertEqual('Var(x)', repr(n))
        self.assertEqual('x', str(n))

    def test_expo_init(self):
        n = ExpoNode(VarNode('x'), NumNode(3))

        self.assertEqual('Expo(Var(x), Num(3))', repr(n))
        self.assertEqual('x^3', str(n))

        m = ExpoNode(VarNode('y'), n)

        self.assertEqual('y^x^3', str(m))

    def test_log_init(self):
        n = LogNode(NumNode(2), TermNode([ExpoNode(VarNode('x'), NumNode(2)), NumNode(2)]))

        self.assertEqual('log(2)_(x^2 + 2)', str(n))

    def test_term_init(self):
        n = NumNode(-5)
        t = TermNode([n])

        self.assertEqual('Term([Num(-5)])', repr(t))

    def test_factor_init(self):
        n = VarNode('x')
        d = TermNode([VarNode('y'), NumNode(-1)])
        f = FactorNode([n], [d])

        self.assertEqual('Factor(1 * Var(x) / 1 * Term([Var(y), Num(-1)]))', repr(f))


class MathNodeAddTest(unittest.TestCase):
    def test_num_add(self):
        n = NumNode(1) + NumNode(-3)

        self.assertEqual('1 - 3', str(n))

    def test_var_add(self):
        n = VarNode('x') + VarNode('y') + NumNode(-2)

        self.assertEqual('x + y - 2', str(n))

    def test_expo_add(self):
        n = ExpoNode(VarNode('x'), NumNode('pi'))
        m = VarNode('y')
        t = n + m

        self.assertEqual('x^pi + y', str(t))

    def test_term_add_1(self):
        n = TermNode([VarNode('x'), NumNode('e')])
        m = TermNode([ExpoNode(VarNode('y'), NumNode(2))])
        t = n + m

        self.assertEqual('y^2 + x + e', str(t))

    def test_term_add_2(self):
        n = LogNode(NumNode('e'), FactorNode([VarNode('x'), VarNode('y')]))
        m = TermNode([VarNode('x'), ExpoNode(VarNode('z'), NumNode(4))])
        t = n + m

        self.assertEqual('z^4 + x + log(e)_(x*y)', str(t))

    def test_factor_add(self):
        n = FactorNode([VarNode('x'), NumNode(3)])
        m = FactorNode([ExpoNode(VarNode('y'), VarNode('x')),
                        TriNode('sin', VarNode('x'))])
        f = n + m

        self.assertEqual('3*x + y^x*sin(x)', str(f))


class MathNodeMulTest(unittest.TestCase):
    def test_num_mul(self):
        n = NumNode(3)
        m = NumNode(2)
        f = n * m

        # TODO: need to do simplify
        self.assertEqual('Num(6)', repr(f))

    def test_var_mul(self):
        n = VarNode('x')
        m = VarNode('k')
        c = NumNode('e')
        f = n * m * c

        self.assertEqual('e*k*x', str(f))


if __name__ == '__main__':
    unittest.main()

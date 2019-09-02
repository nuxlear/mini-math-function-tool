import unittest

from mathlib.tree.math_node import *
from mathlib import math


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

        self.assertEqual('y^(x^3)', str(m))

    def test_log_init(self):
        n = LogNode(NumNode(2), TermNode([ExpoNode(VarNode('x'), NumNode(2)), NumNode(2)]))

        self.assertEqual('log(2)_(x^2 + 2)', str(n))

    def test_term_init(self):
        n = NumNode(-5)
        t = TermNode([n])

        self.assertEqual('Term([Num(-5)])', repr(t))
        self.assertEqual('Num(-5)', repr(t.simplify()))

    def test_factor_init(self):
        n = VarNode('x')
        d = TermNode([VarNode('y'), NumNode(-1)])
        f = FactorNode([n], [d])

        self.assertEqual('Factor(1 * [Var(x)] / 1 * [Term([Var(y), Num(-1)])])', repr(f))
        self.assertEqual('x/(y - 1)', str(f))


class MathNodeAddTest(unittest.TestCase):
    def test_num_add(self):
        n = NumNode(1) + NumNode(-3)

        self.assertEqual('-2', str(n))

    def test_var_add(self):
        n = VarNode('x') + VarNode('y') + NumNode(-2)

        self.assertEqual('x + y - 2', str(n))

    def test_expo_add(self):
        n = ExpoNode(VarNode('x'), NumNode('pi'))
        m = VarNode('y')
        t = n + m

        self.assertEqual('x^pi + y', str(t))

    def test_term_add_1(self):
        """ check for merging TermNodes in __add__ """
        n = TermNode([VarNode('x'), NumNode('e')])
        m = TermNode([ExpoNode(VarNode('y'), NumNode(2))])
        t = n + m

        self.assertEqual('y^2 + x + e', str(t))

    def test_term_add_2(self):
        """ check for adding TermNode and another """
        n = LogNode(NumNode('e'), FactorNode([VarNode('x'), VarNode('y')]))
        m = TermNode([VarNode('x'), ExpoNode(VarNode('z'), NumNode(4))])
        t = n + m

        self.assertEqual('z^4 + x + log(e)_(x*y)', str(t))

    def test_factor_add(self):
        """ check for adding FactorNodes """
        n = FactorNode([VarNode('x'), NumNode(3)])
        m = FactorNode([ExpoNode(VarNode('y'), VarNode('x')),
                        TriNode('sin', VarNode('x'))])
        f = n + m

        self.assertEqual('3*x + y^x*sin(x)', str(f))

    def test_general_add(self):
        """ check for adding inverses """
        n = VarNode('x')
        m = VarNode('x') * -1
        f = n + m

        f = f.merge_similar()
        self.assertEqual('0', str(f.simplify()))


class MathNodeMulTest(unittest.TestCase):
    def test_num_mul(self):
        n = NumNode(3)
        m = NumNode(2)
        f = n * m

        self.assertEqual('Num(6)', repr(f))

    def test_var_mul(self):
        n = VarNode('x')
        m = VarNode('k')
        c = NumNode('e')
        f = n * m * c

        self.assertEqual('e*k*x', str(f))

    def test_factor_mul_1(self):
        """ check for relocation of fractions """
        n = FactorNode()
        m = ExpoNode(VarNode('x'), NumNode(-1))
        f = n * m

        self.assertEqual('1/x', str(f))

    def test_factor_mul_2(self):
        """ check for merging FactorNodes in __mul__ """
        n = FactorNode([VarNode('x'), ExpoNode(NumNode('e'), VarNode('x'))])
        m = FactorNode([], [TermNode([VarNode('x'), NumNode(1)])])
        f = n * m

        self.assertEqual('x*e^x/(x + 1)', str(f))


class MathNodeSimplifyTest(unittest.TestCase):
    def test_expo_simplify(self):
        n = ExpoNode(NumNode('e'), LogNode(NumNode('e'), VarNode('x')))
        m = n.simplify()

        self.assertEqual(VarNode('x'), m)

    def test_log_simplify(self):
        n = LogNode(VarNode('y'),
                    ExpoNode(VarNode('y'), TermNode([VarNode('x'), NumNode(4)])))
        m = n.simplify()

        self.assertEqual(TermNode([VarNode('x'), NumNode(4)]), m)

    def test_factor_simplify_1(self):
        """ check for FactorNode with coefficient only """
        n = FactorNode(coef=(3, 5))
        m = n.simplify()

        self.assertEqual(NumNode(0.6), m)

    def test_factor_simplify_2(self):
        """ check for identity of simplifying FactorNode """
        n = FactorNode([TermNode([VarNode('x'), NumNode(-3)])])
        m = n.simplify()

        self.assertEqual(TermNode([VarNode('x'), NumNode(-3)]), m)

    def test_factor_simplify_3(self):
        """ check for merging FactorNodes and abbreviation """
        n = FactorNode([VarNode('x'), NumNode(7), ExpoNode(VarNode('y'), NumNode(3))],
                       [VarNode('x')])
        m = FactorNode([ExpoNode(NumNode('e'), VarNode('x'))], [n])

        self.assertEqual('e^x/(7*y^3)', str(m.simplify().merge_similar().simplify()))

    def test_factor_simplify_4(self):
        """ check for merging inside of numerators """
        n = FactorNode([VarNode('x'), VarNode('x'),
                        ExpoNode(VarNode('x'), NumNode(4)),
                        ExpoNode(VarNode('x'), NumNode(-2))])

        self.assertEqual('x^4', str(n.simplify().merge_similar().simplify()))

    def test_factor_simplify_5(self):
        """ check for relocation and simplification """
        n = FactorNode([], [ExpoNode(VarNode('x'),
                                     FactorNode([
                                         TermNode([VarNode('y'), VarNode('z'), NumNode(2)]),
                                         NumNode(-1)])
                                     )])

        self.assertEqual('x^(y + z + 2)', str(n.simplify().merge_similar()))

    def test_term_simplify_1(self):
        n = TermNode()
        m = n.simplify()

        self.assertEqual(NumNode(0), m)

    def test_term_simplify_2(self):
        n = TermNode([VarNode('x'), ExpoNode(VarNode('x'), NumNode(2))])
        m = TermNode([LogNode(NumNode('e'), TermNode([VarNode('x'), NumNode(-1)]))])
        t = TermNode([n, m]).simplify()

        self.assertEqual('x^2 + x + log(e)_(x - 1)', str(t))

    def test_term_simplify_3(self):
        n = TermNode([VarNode('x'), VarNode('x')])

        self.assertEqual('2*x', str(n.simplify().merge_similar()))


class MathNodeDerivativeTest(unittest.TestCase):
    def test_derivative_1(self):
        n = LogNode(NumNode(2), TermNode([VarNode('x'), NumNode(-1)]))
        m = n.derivative('x').simplify().merge_similar().simplify()

        self.assertEqual('1/(log(e)_(2)*(x - 1))', str(m))

    def test_derivative_2(self):
        n = TriNode('sin', ExpoNode(NumNode('e'), VarNode('y')))
        m = n.derivative('y').simplify().merge_similar().simplify()

        self.assertEqual('e^y*cos(e^y)', str(m))


class MathNodeEvalTest(unittest.TestCase):
    def test_eval_1(self):
        n = TermNode([ExpoNode(VarNode('x'), NumNode(3)),
                      LogNode(NumNode('e'), TermNode([VarNode('y'), NumNode(2)]))])
        v = n.eval(x=3, y=math.e)

        self.assertEqual(28.55144471393205, v)

    def test_eval_2(self):
        """ check NaN when dividing by zero """
        n = FactorNode([], [VarNode('x')])
        v = n.eval(x=0)

        self.assertEqual('nan', str(v))


if __name__ == '__main__':
    unittest.main()

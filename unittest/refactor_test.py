import unittest

from mathlib import default_lexer_grammar, default_parser_grammar
from mathlib.io import *
from mathlib.tree.builder import *
from mathlib.tree.calculator import *


class MathNodeBuildTest(unittest.TestCase):

    @classmethod
    def setUp(self) -> None:
        self.lexer = Lexer(default_lexer_grammar)
        self.parser = Parser(default_parser_grammar, self.lexer)
        self.builder = NodeBuilder()
        
    @classmethod
    def parse_string(self, string) -> MathNode:
        tokens = self.lexer.stream(string)
        parsed_tree = self.parser.parse(tokens)
        math_tree = self.builder.build(parsed_tree)
        return math_tree.simplify()

    def test_build_1(self):
        s = 'x^2 + 2 + y'
        n = self.parse_string(s)

        self.assertEqual('Term([Expo(Var(x), Num(2)), Var(y), Num(2)])', repr(n))

    def test_build_2(self):
        s = '3^5 - loge_x'
        n = self.parse_string(s)

        self.assertEqual('Term([Factor(-1 * [Log(Num(e), Var(x))]), Num(243)])', repr(n))

    def test_build_3(self):
        s = '-5 + 3*x - y^x'
        n = self.parse_string(s)

        self.assertEqual('Term([Factor(3 * [Var(x)]), Factor(-1 * [Expo(Var(y), Var(x))]), Num(-5)])', repr(n))


class MathNodeCanonicalTest(unittest.TestCase):

    @classmethod
    def setUp(self) -> None:
        self.lexer = Lexer(default_lexer_grammar)
        self.parser = Parser(default_parser_grammar, self.lexer)
        self.builder = NodeBuilder()

    @classmethod
    def build_math_tree(self, string) -> MathNode:
        tokens = self.lexer.stream(string)
        parsed_tree = self.parser.parse(tokens)
        math_tree = self.builder.build(parsed_tree)
        canonical = math_tree.simplify().merge_similar().simplify()
        return canonical

    def test_canonical_1(self):
        s = 'x/((x-1)/(x-2))'
        n = self.build_math_tree(s)

        self.assertEqual('x*(x - 2)/(x - 1)', str(n))

    def test_canonical_2(self):
        s = 'x*loge_(e^(x - 1))/(x - 1)'
        n = self.build_math_tree(s)

        self.assertEqual('x', str(n))

    def test_canonical_3(self):
        s = '2*x^2 - 5*x*x'
        n = self.build_math_tree(s)

        self.assertEqual('-3*x^2', str(n))


class MathNodeExclusionTest(unittest.TestCase):

    @classmethod
    def setUp(self) -> None:
        self.lexer = Lexer(default_lexer_grammar)
        self.parser = Parser(default_parser_grammar, self.lexer)
        self.builder = NodeBuilder()
        self.calculator = Calculator()

    @classmethod
    def build_tree_exclusion(self, string) -> tuple:
        tokens = self.lexer.stream(string)
        parsed_tree = self.parser.parse(tokens)
        math_tree = self.builder.build(parsed_tree)
        return self.calculator.canonicalize(math_tree)

    def test_exclusion_1(self):
        s = 'loge_x'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual([
            [(VarNode('x'), operator.le, 0)]
        ], e)

    def test_exclusion_2(self):
        s = 'log2_(x+pi)'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual('log(2)_(x + pi)', str(n))
        self.assertEqual([
            [(TermNode([VarNode('x'), NumNode('pi')]), operator.le, 0)]
        ], e)


class MathNodeFinalTest(unittest.TestCase):

    @classmethod
    def setUp(self) -> None:
        self.lexer = Lexer(default_lexer_grammar)
        self.parser = Parser(default_parser_grammar, self.lexer)
        self.builder = NodeBuilder()
        self.calculator = Calculator()

    @classmethod
    def build_tree_exclusion(self, string) -> MathNode:
        tokens = self.lexer.stream(string)
        parsed_tree = self.parser.parse(tokens)
        math_tree = self.builder.build(parsed_tree)
        return self.calculator.canonicalize(math_tree)

    def test_01(self):
        s = 'x^99999*sinx/(x^99998)'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual('x*sin(x)', str(n))
        self.assertEqual([[(VarNode('x'), operator.eq, 0)]], e)

        d = n.derivative('x')
        dn, de = self.calculator.canonicalize(d)

        self.assertEqual('sin(x) + x*cos(x)', str(dn))

    def test_02(self):
        s = '3*x^2*log(e)_(e^x) - x^3 + x^2 - 7*x + 5'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual('2*x^3 + x^2 - 7*x + 5', str(n))
        self.assertEqual([[(ExpoNode(NumNode('e'), VarNode('x')), operator.le, 0)]], e)

        d = n.derivative('x')
        dn, de = self.calculator.canonicalize(d)

        self.assertEqual('6*x^2 + 2*x - 7', str(dn))

    def test_03(self):
        s = 'log(x)_(x^2)'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual('2', str(n))
        self.assertEqual([[(VarNode('x'), operator.le, 0)],
                          [(VarNode('x'), operator.eq, 1)],
                          [(ExpoNode(VarNode('x'), NumNode(2)), operator.le, 0)]], e)

        d = n.derivative('x')
        dn, de = self.calculator.canonicalize(d)

        self.assertEqual('0', str(dn))

    def test_04(self):
        s = 'x^(-3.5) + 1/x^3.5'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual('2/x^3.5', str(n))
        self.assertEqual([[(VarNode('x'), operator.eq, 0)],
                          [(VarNode('x'), operator.lt, 0)]], e)

        d = n.derivative('x')
        dn, de = self.calculator.canonicalize(d)

        self.assertEqual('-7/x^4.5', str(dn))

    def test_05(self):
        s = 'sin(cos(x/pi))'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual('sin(cos(x/pi))', str(n))
        self.assertEqual([], e)

        d = n.derivative('x')
        dn, de = self.calculator.canonicalize(d)

        self.assertEqual('-cos(cos(x/pi))*sin(x/pi)/pi', str(dn))

    def test_06(self):
        s = 'x*tany + y^(2*z^2)'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual('y^(2*z^2) + x*tan(y)', str(n))
        self.assertEqual([[(VarNode('y'), operator.lt, 0),
                           (FactorNode([ExpoNode(VarNode('z'), NumNode(2))], coef=(2, 1)),
                            ExpoNode.check_int, False)],
                          [(VarNode('y'), TriNode.check_mod, 0)]], e)

        d = n.derivative('x')
        dn, de = self.calculator.canonicalize(d)

        self.assertEqual('tan(y)', str(dn))

    def test_07(self):
        s = '(x^y * x^z * x^(-2))^0.5'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual('x^(0.5*(y + z - 2))', str(n))
        self.assertEqual([[(ExpoNode(VarNode('x'),
                                     TermNode([VarNode('y'), VarNode('z'), NumNode(-2)])),
                            operator.lt, 0)],
                          [(VarNode('x'), operator.lt, 0),
                           (FactorNode([TermNode([VarNode('y'), VarNode('z'), NumNode(-2)])],
                                       coef=(0.5, 1)),
                            ExpoNode.check_int, False)]], e)
        # self.assertEqual('(x^(y + z - 2))^0.5', str(n))
        # self.assertEqual([[(ExpoNode(VarNode('x'),
        #                              TermNode([VarNode('y'), VarNode('z'), NumNode(-2)])),
        #                     operator.lt, 0)]], e)

        d = n.derivative('x')
        dn, de = self.calculator.canonicalize(d)

        self.assertEqual('0.5*x^(-1 + 0.5*(y + z - 2))*(y + z - 2)', str(dn))

    def test_08(self):
        s = 'x/(x-1)*x/(x-2)'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual('x^2/((x - 1)*(x - 2))', str(n))
        self.assertEqual([[(TermNode([VarNode('x'), NumNode(-1)]), operator.eq, 0)],
                          [(TermNode([VarNode('x'), NumNode(-2)]), operator.eq, 0)]], e)

        d = n.derivative('x')
        dn, de = self.calculator.canonicalize(d)

        self.assertEqual('2*x/((x - 1)*(x - 2)) - x^2/((x - 1)^2*(x - 2)) - x^2/((x - 2)^2*(x - 1))', str(dn))

    def test_09(self):
        s = '(x-y)^2 + sinx*sinx - logy_x'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual('(x - y)^2 + (sin(x))^2 - log(y)_(x)', str(n))
        self.assertEqual([[(VarNode('y'), operator.le, 0)],
                          [(VarNode('y'), operator.eq, 1)],
                          [(VarNode('x'), operator.le, 0)]], e)

        d = n.derivative('x')
        dn, de = self.calculator.canonicalize(d)

        self.assertEqual('2*(x - y) + 2*sin(x)*cos(x) - 1/(x*log(e)_(y))', str(dn))

    def test_10(self):
        s = 'e^loge_x/((x-1)/(x+1))'
        n, e = self.build_tree_exclusion(s)

        self.assertEqual('x*(x + 1)/(x - 1)', str(n))
        # self.assertEqual([[(TermNode([VarNode('x'), NumNode(1)]), operator.eq, 0)]], e)

        d = n.derivative('x')
        dn, de = self.calculator.canonicalize(d)

        self.assertEqual('(x + 1)/(x - 1) + x/(x - 1) - x*(x + 1)/(x - 1)^2', str(dn))


if __name__ == '__main__':
    unittest.main()

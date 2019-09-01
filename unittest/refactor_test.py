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
    def parse_string(self, string) -> ParseNode:
        tokens = self.lexer.stream(string)
        parsed_tree = self.parser.parse(tokens)
        math_tree = self.builder.build(parsed_tree)
        return math_tree

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

    @classmethod
    def build_math_tree(self, string) -> MathNode:
        tokens = self.lexer.stream(string)
        parsed_tree = self.parser.parse(tokens)
        math_tree = self.builder.build(parsed_tree)
        canonical = math_tree.simplify().merge_similar().simplify()
        return canonical

    def test_01(self):
        s = 'x^99999*sinx/(x^99998)'
        n = self.build_math_tree(s)

        self.assertEqual('x*sin(x)', str(n))

    def test_02(self):
        s = '3*x^2*log(e)_(e^x) - x^3 + x^2 - 7*x + 5'
        n = self.build_math_tree(s)

        self.assertEqual('2*x^3 + x^2 - 7*x + 5', str(n))

    def test_03(self):
        s = 'log(x)_(x^2)'
        n = self.build_math_tree(s)

        self.assertEqual('2', str(n))

    def test_04(self):
        s = 'x^(-3.5) + 1/x^3.5'
        n = self.build_math_tree(s)

        self.assertEqual('2/x^3.5', str(n))

    def test_05(self):
        s = 'sin(cos(x/pi))'
        n = self.build_math_tree(s)

        self.assertEqual('sin(cos(x/pi))', str(n))

    def test_06(self):
        s = 'x*tany + y^(2*z^2)'
        n = self.build_math_tree(s)

        self.assertEqual('y^(2*z^2) + x*tan(y)', str(n))

    def test_07(self):
        s = '(x^y * x^z * x^(-2))^0.5'
        n = self.build_math_tree(s)

        self.assertEqual('(x^(y + z - 2))^0.5', str(n))

    def test_08(self):
        s = 'x/(x-1)*x/(x-2)'
        n = self.build_math_tree(s)

        self.assertEqual('x^2/((x - 1)*(x - 2))', str(n))

    def test_09(self):
        s = '(x-y)^2 + sinx*sinx - logy_x'
        n = self.build_math_tree(s)

        self.assertEqual('(x - y)^2 + (sin(x))^2 - log(y)_(x)', str(n))

    def test_10(self):
        s = 'e^loge_x/((x-1)/(x+1))'
        n = self.build_math_tree(s)

        self.assertEqual('x*(x + 1)/(x - 1)', str(n))


if __name__ == '__main__':
    unittest.main()

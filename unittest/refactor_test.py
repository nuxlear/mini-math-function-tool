import unittest

from mathlib import default_lexer_grammar, default_parser_grammar
from mathlib.io import *
from mathlib.tree.builder import *


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


if __name__ == '__main__':
    unittest.main()

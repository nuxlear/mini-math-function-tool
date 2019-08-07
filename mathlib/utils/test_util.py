from mathlib.io.lexer import Lexer
from mathlib.io.parser import Parser
from mathlib.core.node_util import *


def notation_test(string):
    l = Lexer('../mathlib/io/lexer_grammar')
    p = Parser('../mathlib/io/parser_grammar', l)

    tree = p.parse(l.stream(string))

    n = NodeBuilder().build(tree)
    print('Received:\n\t{}\n\t{}'.format(repr(n), n))
    s = NodeSimplifier().canonicalize(n)
    print('Canonicalize:\n\t{}\n\t{}'.format(repr(s), s))
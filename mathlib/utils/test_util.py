from mathlib.io.lexer import Lexer
from mathlib.io.parser import Parser
from mathlib.core.builder import *
from mathlib.core.simplifier import *


def notation_test(string):
    l = Lexer('../mathlib/io/lexer_grammar')
    p = Parser('../mathlib/io/parser_grammar', l)

    tree = p.parse(l.stream(string))

    n = NodeBuilder().build(tree)
    print('Received:\n\t{}\n\t{}'.format(repr(n), n))
    s, e = NodeSimplifier().canonicalize(n)
    print('\nCanonicalize:\n\t{}\n\t{}'.format(repr(s), s))
    print('\nExclusion')
    for x in e:
        print(x)

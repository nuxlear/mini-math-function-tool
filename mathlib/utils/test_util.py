from mathlib.io.lexer import Lexer
from mathlib.io.parser import Parser
from mathlib.core.builder import *
from mathlib.core.simplifier import *
from mathlib.core.calculator import *


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
    print()


def calculation_test(string, **kwargs):
    l = Lexer('../mathlib/io/lexer_grammar')
    p = Parser('../mathlib/io/parser_grammar', l)

    tree = p.parse(l.stream(string))

    n = NodeBuilder().build(tree)
    s, e = NodeSimplifier().canonicalize(n)
    c = Calculator()
    print('Result of {}: {}'.format(', '.join([
        '{}={}'.format(k, v) for k, v in kwargs.items()]),
        c.eval(s, e, **kwargs)))
    print()


def derivation_test(string, var):
    l = Lexer('../mathlib/io/lexer_grammar')
    p = Parser('../mathlib/io/parser_grammar', l)

    tree = p.parse(l.stream(string))

    n = NodeBuilder().build(tree)
    s, e = NodeSimplifier().canonicalize(n)
    c = Calculator()

    dn, de = c.derivate(s, e, var)
    print('\nDerivative:\n\t{}\n\t{}'.format(repr(dn), dn))
    print('\nExclusion')
    for x in de:
        print(x)
    print()

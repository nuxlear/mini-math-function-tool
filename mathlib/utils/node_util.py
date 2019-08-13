import abc
import math
import functools

from mathlib.core.node import *


def negate(node: MathNode):
    if node.__class__ in [int, float]:
        return -node
    elif isinstance(node, NumNode):
        # node.value *= -1
        return NumNode(node.value * -1)
    elif isinstance(node, TermNode):
        # node.factors = [negate(f) for f in node.factors]
        return TermNode([negate(f) for f in node.factors])
    elif isinstance(node, FactorNode):
        # node.coef = -node.coef[0], node.coef[1]
        return FactorNode(node.numerator, node.denominator,
                          (-node.coef[0], node.coef[1]))
    else:
        return FactorNode([node], [], (-1, 1))


def is_negative(node: MathNode):
    if isinstance(node, FactorNode):
        return node.coef[0] / node.coef[1] < 0
    if isinstance(node, NumNode):
        return node.value < 0
    return False


def compare_dim(a: MathNode, b: MathNode):

    def dim(n: MathNode):
        if isinstance(n, ExpoNode):
            return n.body
        if isinstance(n, PolyNode):
            return n.dim
        return 1

    da, db = dim(a), dim(b)
    if da.__class__ not in [int, float] and db.__class__ not in [int, float]:
        return None, None
    if da.__class__ not in [int, float]:
        return 1, db
    if db.__class__ not in [int, float]:
        return -1, da
    return da - db, da - db


if __name__ == '__main__':
    pass

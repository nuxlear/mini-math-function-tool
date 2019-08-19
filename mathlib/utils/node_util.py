import abc
import math
import functools

from mathlib.core.node import *


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


def get_unique_vars(node: MathNode):
    if isinstance(node, TermNode):
        ans = set()
        for x in node.factors:
            ans.update(get_unique_vars(x))
        return ans
    if isinstance(node, FactorNode):
        ans = set()
        for x in node.numerator + node.denominator:
            ans.update(get_unique_vars(x))
        return ans
    if node.__class__ in [PolyNode, TriNode]:
        return get_unique_vars(node.body)
    if node.__class__ in [ExpoNode, LogNode]:
        return get_unique_vars(node.base).union(get_unique_vars(node.body))
    if isinstance(node, VarNode):
        return {node.name}
    return set()


if __name__ == '__main__':
    pass

from mathlib.core.node import *
import operator


def is_identity(equation) -> bool:
    op_dict = {
        '+': operator.add, '-': operator.sub, '*': operator.mul,
        '/': operator.truediv, '%': operator.mod,
        '<': operator.lt, '>': operator.gt,
        '==': operator.eq, '!=': operator.ne,
        '<=': operator.le, '>=': operator.ge,
    }
    a, op, m, cmp, b = [None] * 5
    if len(equation) == 3:
        a, cmp, b = equation
        if isinstance(a, NumNode):
            a = a.value
    if len(equation) == 5:
        a, op, m, cmp, b = equation
        if isinstance(m, NumNode):
            m = m.value

    if isinstance(a, PolyNode):
        if a.dim % 2 == 0 and b == 0:
            return cmp == '>='

    if a.__class__ in [int, float]:
        if m.__class__ in [int, float]:
            a = op_dict[op](a, m)
        if b.__class__ in [int, float]:
            # return op_dict[cmp](a, b)
            return True
            # if op_dict[cmp](a, b) is True -> invalid equation
    return False


class Calculator:

    def eval(self, **kwargs):
        pass

    def derivate(self, var):
        pass


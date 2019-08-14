from mathlib.core.node import *
from mathlib.core.simplifier import NodeSimplifier
import operator


op_dict = {
    '+': operator.add, '-': operator.sub, '*': operator.mul,
    '/': operator.truediv, '%': operator.mod,
    '<': operator.lt, '>': operator.gt,
    '==': operator.eq, '!=': operator.ne,
    '<=': operator.le, '>=': operator.ge,
    'not': lambda x, t: not isinstance(x, t),
}


class Calculator:

    def __init__(self, simplifier=None):
        self.simplifier = simplifier
        if simplifier is None:
            self.simplifier = NodeSimplifier()

    def eval(self, node: MathNode, exclusion: list, **kwargs):
        for x in exclusion:
            ans = True
            for e in x:
                if len(e) == 3:
                    a, cmp, b = e
                    a = self._eval_node(a, **kwargs)
                if len(e) == 5:
                    a, op, m, cmp, b = e
                    a = self._eval_node(a, **kwargs)
                    m = self._eval_node(m, **kwargs)
                    a = op_dict[op](a, m)

                ans = ans and op_dict[cmp](a, b)
            if ans:
                return math.nan

        result = self._eval_node(node, **kwargs)
        if result == 0:
            return 0.
        return result

    def _eval_node(self, node: MathNode, **kwargs):
        if node.__class__ in [int, float]:
            return node
        if isinstance(node, TermNode):
            ans = 0
            for x in node.factors:
                ans += self._eval_node(x, **kwargs)
            return ans

        if isinstance(node, FactorNode):
            nu, deno = node.coef[0], node.coef[1]
            for x in node.numerator:
                nu *= self._eval_node(x, **kwargs)
            for x in node.denominator:
                deno *= self._eval_node(x, **kwargs)
            if deno == 0:
                # raise ZeroDivisionError('in {}'.format(node))
                return math.nan
            return nu / deno

        if isinstance(node, PolyNode):
            body = self._eval_node(node.body, **kwargs)
            if body < 0 and node.dim % 1 != 0:
                return math.nan
            return body ** node.dim

        if isinstance(node, ExpoNode):
            base = self._eval_node(node.base, **kwargs)
            body = self._eval_node(node.body, **kwargs)
            if base < 0 and body % 1 != 0:
                return math.nan
            return base ** body

        if isinstance(node, LogNode):
            body = self._eval_node(node.body, **kwargs)
            base = self._eval_node(node.base, **kwargs)
            if body <= 0 or base == 1 or base <= 0:
                return math.nan
            return math.log(body, base)

        if isinstance(node, TriNode):
            func_dict = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan}
            body = self._eval_node(node.body, **kwargs)
            if node.func == 'tan' and body % (2*math.pi) == math.pi / 2:
                return math.nan
            return func_dict[node.func](body)

        if isinstance(node, VarNode):
            if node.name not in kwargs:
                raise ArithmeticError('{} is not defined.'.format(node.name))
            return kwargs[node.name]

        if isinstance(node, NumNode):
            return node.value

    def derivate(self, node: MathNode, exclusion: list, var: str):
        n = self._derivate(node, var)
        n, _ex = self.simplifier.canonicalize(n)

        exclusion += _ex

        ex = []
        for e in exclusion:
            if e in ex:
                continue
            ex.append(e)

        return n, ex

    def _derivate(self, node: MathNode, var: str):
        if not self._formular_of(node, var) or isinstance(node, NumNode):
            return NumNode(0)

        if isinstance(node, VarNode):
            return NumNode(1)

        if isinstance(node, TermNode):
            factors = [self._derivate(x, var) for x in node.factors]
            return TermNode(factors)

        if isinstance(node, FactorNode):
            if len(node.numerator) == 0 and len(node.denominator) == 1:
                d = node.denominator[0]
                return FactorNode([self._derivate(d, var)], [PolyNode(d, 2)], (-node.coef[0], node.coef[1]))

            c_nu = [x for x in node.numerator if not self._formular_of(x, var)]
            c_deno = [x for x in node.denominator if not self._formular_of(x, var)]

            nu = [x for x in node.numerator if x not in c_nu]
            deno = [FactorNode([], [x]) for x in node.denominator
                    if x not in c_deno]

            target = nu + deno
            factors = []
            for t in target:
                others = [self._derivate(t, var)] + [x for x in target if x != t]
                factors.append(FactorNode(others + c_nu, c_deno, node.coef))

            return TermNode(factors)

        if isinstance(node, PolyNode):
            if node.dim == 1:
                return self._derivate(node.body, var)
            return FactorNode([PolyNode(node.body, node.dim - 1),
                               self._derivate(node.body, var)], [],
                              (node.dim, 1))

        if isinstance(node, ExpoNode):
            if not self._formular_of(node.base, var):
                # form of a^f(x)
                return FactorNode([node, LogNode(NumNode(math.e), node.base),
                                   self._derivate(node.body, var)])
            if not self._formular_of(node.body, var):
                # form of f(x)^a
                return FactorNode([node.body,
                                  ExpoNode(node.base,
                                           TermNode([node.body, NumNode(-1)]))])
            # form of f(x)^g(x)
            return self._derivate(ExpoNode(NumNode(math.e),
                                           FactorNode([LogNode(NumNode(math.e), node.base),
                                                       node.body])), var)

        if isinstance(node, LogNode):
            if not self._formular_of(node.base, var):
                # form of log(a)_f(x)
                return FactorNode([self._derivate(node.body, var)],
                                  [LogNode(NumNode(math.e), node.base),
                                   node.body])
            return self._derivate(FactorNode([LogNode(NumNode(math.e), node.body)],
                                             [LogNode(NumNode(math.e), node.base)]), var)

        if isinstance(node, TriNode):
            if node.func == 'sin':
                return FactorNode([TriNode('cos', node.body),
                                   self._derivate(node.body, var)])
            if node.func == 'cos':
                return FactorNode([TriNode('sin', node.body),
                                   self._derivate(node.body, var)], [], (-1, 1))
            if node.func == 'tan':
                return FactorNode([self._derivate(node.body, var)],
                                  [PolyNode(TriNode('cos', node.body), 2)])

    def _formular_of(self, node: MathNode, var: str):
        return var in str(node)

    def continuous(self, node: MathNode, exclusion: list, **kwargs):
        value = self.eval(node, exclusion, **kwargs)
        return value is not math.nan

    # def is_undefined(self, node: MathNode, **kwargs):
    #     pass

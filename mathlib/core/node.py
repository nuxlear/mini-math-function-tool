import abc
import math
import functools

from mathlib.core._node import *


class ParseNode:

    def __init__(self, value, type, parent):
        self.value = value
        self.type = type
        self.parent = parent

        self.childs = []

    def add_child(self, node):
        self.childs.append(node)

    def __str__(self):
        if self.is_terminal():
            return '{} -> `{}`'.format(self.type, self.value)
        else:
            return '{} -> [{}]'.format(self.type, ', '.join(map(str, self.childs)))

    def is_terminal(self):
        return self.value is not None


# @functools.total_ordering
# class MathNode:
#
#     order = None
#
#     @abc.abstractmethod
#     def eval(self, **kwargs):
#         pass
#
#     @abc.abstractmethod
#     def similar(self, other):
#         pass
#
#     @abc.abstractmethod
#     def derivate(self, **kwargs):
#         pass
#
#     @abc.abstractmethod
#     def add(self, other):
#         pass
#
#     def __lt__(self, other):
#         if self.__class__ != other.__class__:
#             return self.order < other.order
#         return self._compare(other)
#
#     @abc.abstractmethod
#     def _compare(self, other):
#         pass
#
#
# class NumNode(MathNode):
#
#     order = 0
#
#     def __init__(self, value):
#         self.value = value
#
#     def similar(self, num):
#         return isinstance(num, NumNode)
#
#     def eval(self, **kwargs):
#         return self.value
#
#     def add(self, num):
#         self.value += num.value
#
#     def __str__(self):
#         return str(self.value)
#
#     def _compare(self, num):
#         return self.value < num.value
#
#
# class TermNode(MathNode):
#
#     order = 0
#
#     def __init__(self, factors: list):
#         super(TermNode, self).__init__()
#         self.factors = factors
#
#     def similar(self, term):
#         if not isinstance(term, TermNode):
#             return False
#         ans = True
#         for our, their in zip(self.factors, term.factors):
#             ans = ans and our.similar(their)
#         return ans
#
#     def eval(self, **kwargs):
#         ans = 0
#         for f in self.factors:
#             ans += f.eval(**kwargs)
#         return ans
#
#     def add(self, term):
#         self.factors.extend(term.factors)
#
#     def __str__(self):
#         s = ''
#         for i, f in enumerate(self.factors):
#             nu, deno = f.get_coef()
#             if nu / deno < 0:
#                 s += ' - '
#             elif i > 0:
#                 s += ' + '
#             s += '({})'.format(str(f))
#         return s
#
#
# class FactorNode(MathNode):
#
#     order = 5
#
#     def __init__(self, numerator: list, denominator: list):
#         super(FactorNode, self).__init__()
#         self.numerator = numerator
#         self.denominator = denominator
#
#     def similar(self, factor):
#         # if not isinstance(factor, FactorNode) \
#         #         or len(self.denominator) != len(factor.denominator):
#         #     return False
#         # ans = True
#         # for x, y in zip(self.denominator, factor.denominator):
#         #     ans = ans and x.similar(y)
#         if not isinstance(factor, FactorNode):
#             return False
#         nu, deno = self.get_dim()
#         fnu, fdeno = factor.get_dim()
#         if len(nu) != len(fnu) or len(deno) != len(fdeno):
#             return False
#         ans = True
#         for x, y in zip(nu, fnu):
#             ans = ans and x.similar(y)
#         for x, y in zip(deno, fdeno):
#             ans = ans and x.similar(y)
#         return ans
#
#     def eval(self, **kwargs):
#         numerator, denominator = 1, 1
#         for x in self.numerator:
#             numerator *= x.eval(**kwargs)
#         for x in self.denominator:
#             denominator *= x.eval(**kwargs)
#         return numerator / denominator
#
#     def add(self, factor):
#         nu, deno = self.get_coef()
#         fnu, fdeno = factor.get_coef()
#
#         gcd = math.gcd(deno, fdeno)
#         new_nu = (nu * gcd / deno) + (fnu * gcd / fdeno)
#
#         xnu, xdeno = self.get_dim()
#         if new_nu != 1:
#             xnu.insert(0, NumNode(new_nu))
#         if gcd != 1:
#             xdeno.insert(0, NumNode(gcd))
#         self.numerator = xnu
#         self.denominator = xdeno
#
#     def __str__(self):
#         # TODO: check sign and coef for pretty string
#         abs_str = lambda x: str(abs(x.value) if isinstance(x, NumNode) else x)
#         nu = '*'.join(map(abs_str, self.numerator))
#         if len(self.denominator) > 0:
#             deno = '*'.join(map(abs_str, self.denominator))
#             return '({})/({})'.format(nu, deno)
#         return nu
#
#     def get_coef(self):
#         nu, deno = 1, 1
#         for x in self.denominator:
#             if not isinstance(x, NumNode):
#                 continue
#             if x.value == 0:
#                 raise ZeroDivisionError('denominator of FactorNode `{}` contains 0.'.format(FactorNode))
#             deno *= x.value
#
#         for x in self.numerator:
#             if not isinstance(x, NumNode):
#                 continue
#             if x.value == 0:
#                 self.numerator = self.denominator = []
#                 break
#             nu *= x.value
#
#         return nu, deno
#
#     def get_dim(self):
#         nu = [x for x in self.numerator if not isinstance(x, NumNode)]
#         deno = [x for x in self.denominator if not isinstance(x, NumNode)]
#         return sorted(nu), sorted(deno)
#
#     def _get_order(self):
#         return max([x.order for x in self.numerator]
#                    + [x.order for x in self.denominator] + [0])
#
#     def _compare(self, factor):
#         return self._get_order() < factor._get_order()
#
#
# class BodyNode(MathNode, metaclass=abc.ABCMeta):
#
#     def __init__(self, body, coef=1):
#         self.body = body
#         self.coef = coef
#
#     @abc.abstractmethod
#     def similar(self, other):
#         pass
#
#     def eval(self, **kwargs):
#         return self.coef * self.body.eval(**kwargs)
#
#     # def multiply(self, n):
#     #     self.coef *= n
#     #
#     # def set_coef(self, coef):
#     #     self.coef = coef
#
#
# class PolyNode(BodyNode):
#
#     order = 1
#
#     def __init__(self, body, dim=1, coef=1):
#         super(PolyNode, self).__init__(body, coef)
#         self.dim = dim
#
#     def similar(self, poly):
#         if not isinstance(poly, PolyNode):
#             return False
#         return poly.body.similar(self.body) and poly.dim == self.dim
#
#     def eval(self, **kwargs):
#         return self.coef * (self.body.eval(**kwargs) ** self.dim)
#
#     def __str__(self):
#         s = '({})^{}'.format(self.body, self.dim)
#         if self.coef == -1:
#             return '-{}'.format(s)
#         elif self.coef != 1:
#             return '{}*{}'.format(self.coef, s)
#         return s
#
#     def _compare(self, poly):
#         return self.dim < poly.dim
#
#
# class ExpoNode(BodyNode):
#
#     order = 2
#
#     def __init__(self, base, body, coef=1):
#         super(ExpoNode, self).__init__(body, coef)
#         self.base = base
#
#     def similar(self, expo):
#         if not isinstance(expo, ExpoNode):
#             return False
#         return self.base == expo.base
#
#     def eval(self, **kwargs):
#         return self.coef * (self.base ** self.body.eval(**kwargs))
#
#     def __str__(self):
#         s = '({})^{}'.format(self.base, self.body)
#         if self.coef == -1:
#             return '-{}'.format(s)
#         elif self.coef != 1:
#             return '{}*{}'.format(self.coef, s)
#         return s
#
#     def _compare(self, expo):
#         return self.base < expo.base
#
#
# class LogNode(BodyNode):
#
#     order = 4
#
#     def __init__(self, base, body, coef=1):
#         if isinstance(base, NumNode) and (base.eval() <= 0 or base.eval() == 1):
#             raise ValueError('Invalid base for logarithm: {}'.format(base.eval()))
#
#         super(LogNode, self).__init__(body, coef)
#         self.base = base
#
#     def similar(self, log):
#         if not isinstance(log, LogNode):
#             return False
#         return self.base == log.base
#
#     def eval(self, **kwargs):
#         base = self.base.eval(**kwargs)
#         if base <= 0 or base == 1:
#             raise ValueError('Invalid base for logarithm: {}'.format(base))
#         return self.coef * math.log(self.body.eval(**kwargs), )
#
#     def __str__(self):
#         s = 'log{}_{}'.format(self.base, self.body)
#         if self.coef == -1:
#             return '-{}'.format(s)
#         elif self.coef != 1:
#             return '{}*{}'.format(self.coef, s)
#         return s
#
#     def _compare(self, log):
#         return self.base < log.base
#
#
# class TriNode(BodyNode):
#
#     order = 3
#
#     def __init__(self, func, body, coef=1):
#         super(TriNode, self).__init__(body, coef)
#         self.func = func
#
#     def similar(self, tri):
#         if not isinstance(tri, TriNode):
#             return False
#         return self.func == tri.func
#
#     def eval(self, **kwargs):
#         return self.coef * self.func(self.body.eval(**kwargs))
#
#     def __str__(self):
#         func_str = {math.sin: 'sin', math.cos: 'cos', math.tan: 'tan'}
#         s = '{}{}'.format(func_str[self.func], self.body)
#         if self.coef == -1:
#             return '-{}'.format(s)
#         elif self.coef != 1:
#             return '{}*{}'.format(self.coef, s)
#         return s
#
#     def _compare(self, tri):
#         func_order = {math.sin: 0, math.cos: 1, math.tan: 2}
#         return func_order[self.func] < func_order[tri.func]
#
#
# class VarNode(BodyNode):
#
#     order = 0.5
#
#     def __init__(self, body, coef=1):
#         super(VarNode, self).__init__(body, coef)
#
#     def similar(self, var):
#         if not isinstance(var, VarNode):
#             return False
#         return self.body == var.body
#
#     def eval(self, **kwargs):
#         assert self.body in kwargs, 'undefined variable: {}'.format(self.body)
#         return kwargs[self.body]
#
#     def __str__(self):
#         return str(self.body)
#
#     def _compare(self, var):
#         return self.body < var.body


class NodeBuilder:

    def __init__(self):
        self.math_tree = None

    def build(self, parse_tree: ParseNode):
        self.math_tree = self._traverse(parse_tree)
        return self.math_tree

    def _traverse(self, node: ParseNode) -> MathNode:

        if node.type in ['expr', 'term', 'body']:
            return self._flatten(node)
        if node.type == 'factor':
            prefix, expo = node.childs
            n = self._traverse(expo)
            if len(prefix.childs) > 0:
                self._negate(n)
            return n
        if node.type in ['expo', 'function', 'funbody']:
            if len(node.childs) > 1:
                return self._traverse(node.childs[1])   # ( expr )
            return self._traverse(node.childs[0])
        if node.type == 'triangular':
            func_name = node.childs[0].childs[0].value
            return TriNode(func_name, self._traverse(node.childs[1]))
        if node.type == 'logarithm':
            return LogNode(self._traverse(node.childs[1]), self._traverse(node.childs[3]))
        if node.type == 'var':
            return VarNode(node.childs[0].value)
        if node.type == 'num':
            const_dict = {'pi': math.pi, 'e': math.e}
            val = node.childs[0].value
            if val in const_dict:
                return NumNode(const_dict[val])
            return NumNode(float(val) if '.' in val else int(val))

    def _flatten(self, node: ParseNode):
        cur = node
        if node.type == 'expr':
            factors = [self._traverse(cur.childs[0])]
            cur = cur.childs[1]
            while len(cur.childs) > 0:
                f = self._traverse(cur.childs[1])
                if cur.childs[0].childs[0].value == '-':
                    self._negate(f)
                factors.append(f)
                cur = cur.childs[2]
            if len(factors) == 1:
                return factors[0]
            return TermNode(factors)

        if node.type == 'term':
            nu = [self._traverse(cur.childs[0])]
            deno = []
            cur = cur.childs[1]
            while len(cur.childs) > 0:
                op = cur.childs[0].childs[0].value
                n = self._traverse(cur.childs[1])
                if op == '*':
                    nu.append(n)
                if op == '/':
                    deno.append(n)
                cur = cur.childs[2]
            if len(nu) == 1 and len(deno) == 0:
                if isinstance(nu[0], VarNode):
                    return FactorNode(nu, [])
                return nu[0]
            return FactorNode(nu, deno)

        # TODO: fix along with parser_grammar
        if node.type == 'body':
            base = self._traverse(cur.childs[0])
            cur = cur.childs[1]
            while len(cur.childs) > 0:
                n = self._traverse(cur.childs[1])
                if isinstance(base, NumNode):
                    if isinstance(n, NumNode):
                        base = NumNode(base.value ** n.value)
                    else:
                        base = ExpoNode(base, n)
                else:
                    if isinstance(n, NumNode):
                        base = PolyNode(base, n.value)
                    else:
                        base = ExpoNode(base, n)
                cur = cur.childs[2]
            return FactorNode([base], [])

    def _negate(self, node: MathNode):
        if isinstance(node, NumNode):
            node.value *= -1
        if isinstance(node, TermNode):
            for f in node.factors:
                self._negate(f)
        if isinstance(node, FactorNode):
            node.coef = -node.coef[0], node.coef[1]


class NodeSimplifier:

    def canonicalize(self, node: MathNode):
        node = self._expand(node)
        node = self._merge_similar(node)
        node = self._remove_zeros(node)
        self._sort(node)
        return node

    def _expand(self, node):
        return node

    def _merge_similar(self, node: MathNode):
        self._sort(node)
        if isinstance(node, TermNode):
            factors = self._merge_add([self._merge_similar(x) for x in node.factors])
            return TermNode(factors)
        # if isinstance(node, FactorNode):
            # nu = self._merge_mul([self._merge_similar(x) for x in node.numerator])
            # deno = self._merge_mul([self._merge_similar(x) for x in node.denominator])
            # return FactorNode(nu, deno)
        return node
        # if isinstance(node, TermNode):
        #     sim_list = []
        #     for x in node.factors:
        #         self._merge_similar(x)
        #         for s in sim_list:
        #             if s.similar(x):
        #                 s += x
        #                 break
        #         else:
        #             sim_list.append(x)
        #     node.factors = sim_list
        # if isinstance(node, FactorNode):
        #     sim_list = []
        #     for x in node.numerator:
        #         self._merge_similar(x)
        #         for s in sim_list:
        #             if s.similar(x):

    def _merge_add(self, node_list: list) -> list:
        node_list = [x for x in node_list if x is not None]
        sim_list = []
        for x in node_list:
            for s in sim_list:
                if s.similar(x):
                    s += x
                    break
            else:
                sim_list.append(x)
        return sim_list

    def _merge_mul(self, node_list: list) -> list:
        node_list = [x for x in node_list if x is not None]
        sim_list = []
        for x in node_list:
            q = [x for x in sim_list]
            while len(q) > 0:
                cur = q.pop(0)
                if q.similar(x):
                    pass
        return node_list

    def _remove_zeros(self, node: MathNode):
        if isinstance(node, TermNode):
            node.factors = [x for x in node.factors if not self._is_zero(x)]
        return node

    def _is_zero(self, node: MathNode):
        if isinstance(node, TermNode):
            return len(node.factors) == 0
        if isinstance(node, FactorNode):
            if node.coef[0] == 0:
                return True
            for x in node.numerator:
                if self._is_zero(x):
                    return True
            return False
        if isinstance(node, NumNode):
            return node.value == 0
        if isinstance(node, PolyNode):
            return self._is_zero(node.body)
        if isinstance(node, ExpoNode):
            return self._is_zero(node.base)
        return False
        # if isinstance(node, LogNode):
        #     return self._is_one(node.body)
        # if isinstance(node, TriNode):
        #     return node.func in ['sin', 'tan'] and self._is_zero(node.body) \
        #         or node.func == 'cos' and self._is_one(node.body)

    def _sort(self, node: MathNode):
        if isinstance(node, TermNode):
            for x in node.factors:
                self._sort(x)
            node.factors.sort()
        if isinstance(node, FactorNode):
            for x in node.numerator + node.denominator:
                self._sort(x)
            node.numerator.sort()
            node.denominator.sort()


if __name__ == '__main__':
    pass

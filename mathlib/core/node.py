import abc
import math


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


class MathNode:

    @abc.abstractmethod
    def eval(self, **kwargs):
        pass

    @abc.abstractmethod
    def similar(self, other):
        pass

    @abc.abstractmethod
    def derivate(self, **kwargs):
        pass

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class NumNode(MathNode):

    def __init__(self, value):
        self.value = value

    def eval(self, **kwargs):
        return self.value


class TermNode(MathNode):

    def __init__(self, ops: list, factors: list):
        assert len(ops) == len(factors), 'the number of operations and factors are not equal.'

        super(TermNode, self).__init__()
        self.ops = ops
        self.factors = factors

    def similar(self, term):
        if not isinstance(term, TermNode):
            return False
        ans = self.ops == term.ops
        for our, their in zip(self.factors, term.factors):
            ans = ans and our == their
        return ans

    def eval(self, **kwargs):
        ans = 0
        for op, factor in zip(self.ops, self.factors):
            ans = op(ans, factor.eval(**kwargs))
        return ans


class FactorNode(MathNode):

    # TODO: fill this class for (exprs)/(exprs) notation
    def __init__(self, ):
        pass


class BodyNode(MathNode, metaclass=abc.ABCMeta):

    def __init__(self, body, coef=1):
        self.body = body
        self.coef = coef

    @abc.abstractmethod
    def similar(self, other):
        pass

    def eval(self, **kwargs):
        return self.coef * self.body.eval(**kwargs)

    def multiply(self, n):
        self.coef *= n

    def set_coef(self, coef):
        self.coef = coef


class PolyNode(BodyNode):

    def __init__(self, body, coef=1, dim=1):
        super(PolyNode, self).__init__(body, coef)
        self.dim = dim

    def similar(self, poly):
        if not isinstance(poly, PolyNode):
            return False
        return poly.body.similar(self.body) and poly.dim == self.dim

    def eval(self, **kwargs):
        return self.coef * (self.body.eval(**kwargs) ** self.dim)


class ExpoNode(BodyNode):

    def __init__(self, base, body, coef=1):
        super(ExpoNode, self).__init__(body, coef)
        self.base = base

    def similar(self, expo):
        if not isinstance(expo, ExpoNode):
            return False
        return self.base == expo.base

    def eval(self, **kwargs):
        return self.coef * (self.base ** self.body.eval(**kwargs))


class LogNode(BodyNode):

    def __init__(self, base, body, coef=1):
        if base.eval() <= 0 or base.eval() == 1:
            raise ValueError('Invalid base for logarithm: {}'.format(base))

        super(LogNode, self).__init__(body, coef)
        self.base = base

    def similar(self, log):
        if not isinstance(log, LogNode):
            return False
        return self.base == log.base

    def eval(self, **kwargs):
        return self.coef * math.log(self.body.eval(**kwargs), self.base)


class TriNode(BodyNode):

    def __init__(self, func, body, coef=1):
        super(TriNode, self).__init__(body, coef)
        self.func = func

    def similar(self, tri):
        if not isinstance(tri, TriNode):
            return False
        return self.func == tri.func

    def eval(self, **kwargs):
        return self.coef * self.func(self.body.eval(**kwargs))


class VarNode(BodyNode):

    def __init__(self, body, coef=1):
        super(VarNode, self).__init__(body, coef)

    def similar(self, var):
        if not isinstance(var, VarNode):
            return False
        return self.body == var.body

    def eval(self, **kwargs):
        assert self.body in kwargs, 'undefined variable: {}'.format(self.body)
        return kwargs[self.body]


class NodeBuilder:

    def __init__(self):
        self.math_tree = None

    def build(self, parse_tree):
        # self.math_tree = self._traverse(parse_tree)
        pass

    def _canonicalize(self, tree):
        pass

    def _traverse(self, node: ParseNode) -> MathNode:

        if node.type in ['expr', 'term', 'factor']:
            # TODO: chaining all -tails with TermNode / FactorNode / ExpoNode
            pass
        if node.type == 'expo':
            prefix, body = node.childs
            n = self._traverse(body)
            # TODO: need to apply prefix (minus) or coefficient
            if len(prefix.childs) > 0:
                pass
            return n
        if node.type in ['body', 'function', 'funbody']:
            if len(node.childs) > 1:
                return self._traverse(node.childs[1])   # ( expr )
            return self._traverse(node.childs[0])
        if node.type == 'triangular':
            func_dict = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan}
            func_name = node.childs[0].childs[0].value
            return TriNode(func_dict[func_name], self._traverse(node.childs[1]))
        if node.type == 'logarithm':
            return LogNode(self._traverse(node.childs[1]), self._traverse(node.childs[3]))
        if node.type == 'var':
            return VarNode(node.value)
        if node.type == 'num':
            return NumNode(node.value)

    def _flatten(self, node: ParseNode):
        pass



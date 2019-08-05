import abc
import math
import functools


@functools.total_ordering
class MathNode(metaclass=abc.ABCMeta):
    order = None

    @abc.abstractmethod
    def similar(self, other) -> bool:
        pass

    def __lt__(self, other):
        if self.__class__ != other.__class__:
            return self.order < other.order
        return self._compare(other)

    @abc.abstractmethod
    def _compare(self, other) -> bool:
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    def __add__(self, other):
        if not self.similar(other):
            raise ArithmeticError('adding `{}` and `{}` is not defined'.format(self, other))
        self._merge(other)

    @abc.abstractmethod
    def _merge(self, other) -> None:
        pass

    # @abc.abstractmethod
    # def __sub__(self, other):
    #     pass
    #
    # @abc.abstractmethod
    # def __mul__(self, other):
    #     pass
    #
    # @abc.abstractmethod
    # def __truediv__(self, other):
    #     pass
    #
    # @abc.abstractmethod
    # def __neg__(self):
    #     pass


class NumNode(MathNode):
    order = 0

    def __init__(self, value):
        self.value = value

    def similar(self, other):
        return isinstance(other, NumNode)

    def __str__(self):
        return 'Num({})'.format(self.value)

    def _compare(self, other):
        return self.value < other.value

    def _merge(self, other):
        self.value += other.value


class TermNode(MathNode):
    order = -1

    def __init__(self, factors: list):
        super(TermNode, self).__init__()
        self.factors = sorted(factors)

    def similar(self, other):
        if not isinstance(other, TermNode) \
                or len(self.factors) != len(other.factors):
            return False
        ans = True
        for s, o in zip(self.factors, other.factors):
            ans = ans and s.similar(o)
        return ans

    def __str__(self):
        return 'Term({})'.format(', '.join(map(str, self.factors)))

    def _compare(self, other):
        return len(self.factors) < len(other.factors)

    def _merge(self, other):
        self.factors.extend(other.factors)


class FactorNode(MathNode):
    order = 5

    def __init__(self, numerator: list, denominator: list, coef=(1, 1)):
        super(FactorNode, self).__init__()
        self.numerator = sorted(numerator)
        self.denominator = sorted(denominator)

        if coef[1] % 1 != 0:    # coef[1] is not `int`
            self.coef = coef[0] / coef[1], 1
        else:
            self.coef = coef

    def similar(self, other):
        if not isinstance(other, FactorNode):
            return False
        nu, deno = self._get_dim()
        fnu, fdeno = other._get_dim()
        if len(nu) != len(fnu) or len(deno) != len(fdeno):
            return False
        ans = True
        for x, y in zip(nu, fnu):
            ans = ans and x.similar(y)
        for x, y in zip(deno, fdeno):
            ans = ans and x.similar(y)
        return ans

    def __str__(self):
        return 'Factor({} * {} / {} * {})' \
            .format(self.coef[0], ', '.join(map(str, self.numerator)),
                    self.coef[1], ', '.join(map(str, self.denominator)))

    def _compare(self, other):
        return self._get_order() < other._get_order()

    def _get_dim(self):
        return self.numerator, self.denominator

    def _get_order(self):
        return max([x.order for x in self.numerator]
                   + [x.order for x in self.denominator] + [0])

    def _merge(self, other):
        a, b = self.coef
        c, d = other.coef

        gcd = math.gcd(b, d)
        nu = (a * gcd / b) + (b * gcd / d)
        self.coef = (nu, gcd)


class PolyNode(MathNode):
    order = 5

    def __init__(self, body, dim=1):
        super(PolyNode, self).__init__()
        self.body = body
        self.dim = dim

    def similar(self, other):
        if not isinstance(other, PolyNode):
            return False
        return other.body.similar(self.body) and other.dim == self.dim

    def __str__(self):
        return 'Poly({}, {})'.format(self.body, self.dim)

    def _compare(self, other):
        return self.dim < other.dim

    def _merge(self, other):
        # self.body += other.body
        pass


class ExpoNode(MathNode):
    order = 2

    def __init__(self, base, body):
        super(ExpoNode, self).__init__()
        self.base = base
        self.body = body

    def similar(self, other):
        if not isinstance(other, ExpoNode):
            return False
        return self.base == other.base  # maybe need to use `equal`

    def __str__(self):
        return 'Expo({}, {})'.format(self.base, self.body)

    def _compare(self, other):
        return self.base < other.base

    def _merge(self, other):
        # ..?
        pass


class LogNode(MathNode):
    order = 4

    def __init__(self, base, body):
        if isinstance(base, NumNode) and (base.value <= 0 or base.value == 1):
            raise ValueError('Invalid base for logarithm: {}'.format(base.value))

        super(LogNode, self).__init__()
        self.base = base
        self.body = body

    def similar(self, other):
        if not isinstance(other, LogNode):
            return False
        return self.base == other.base

    def __str__(self):
        return 'Log({}, {})'.format(self.base, self.body)

    def _compare(self, other):
        return self.base < other.base

    def _merge(self, other):
        self.body = TermNode([FactorNode([self.body, other.body], [])])


class TriNode(MathNode):
    order = 3

    def __init__(self, func, body):
        super(TriNode, self).__init__()
        self.func = func
        self.body = body

    def similar(self, other):
        if not isinstance(other, TriNode):
            return False
        return self.func == other.func

    def __str__(self):
        func = self.func[0].upper() + self.func[1:]
        return '{}({})'.format(func, self.body)

    def _compare(self, other):
        func_order = {'sin': 0, 'cos': 1, 'tan': 2}
        return func_order[self.func] < func_order[other.func]

    def _merge(self, other):
        # ???
        pass


class VarNode(MathNode):
    order = 0.5

    def __init__(self, name):
        super(VarNode, self).__init__()
        self.name = name

    def similar(self, other):
        if not isinstance(other, VarNode):
            return False
        return self.name == other.name

    def __str__(self):
        return self.name

    def _compare(self, other):
        return self.name < other.name

    def _merge(self, other):
        # ???
        pass


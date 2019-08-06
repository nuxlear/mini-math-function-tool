import abc
import math
import functools


@functools.total_ordering
class MathNode(metaclass=abc.ABCMeta):
    order = None
    #
    # def __init__(self):
    #     self.parent = None

    @abc.abstractmethod
    def similar(self, other) -> bool:
        pass

    def __lt__(self, other):
        if self.__class__ != other.__class__:
            return self.order < other.order
        return self._compare(other)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other.__dict__

    @abc.abstractmethod
    def _compare(self, other) -> bool:
        pass

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    def __add__(self, other):
        if not self.similar(other):
            raise ArithmeticError('adding `{}` and `{}` is not defined'.format(self, other))
        return self._add(other)

    def __mul__(self, other):
        # if not self.similar(other):
        #     if isinstance(other, FactorNode):
        #         return FactorNode([self] + other.numerator, other.denominator)
        #     if isinstance(other, list):
        #         return [self] + other
        #     return FactorNode([self, other], [])
        if not self.similar(other):
            raise ArithmeticError('multiplying `{}` and `{}` is not defined'.format(self, other))
        return self._mul(other)

    @abc.abstractmethod
    def _add(self, other) -> None:
        pass

    @abc.abstractmethod
    def _mul(self, other) -> None:
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
    order = 7

    def __init__(self, value):
        self.value = value

    def similar(self, other):
        return isinstance(other, NumNode)

    def __repr__(self):
        return 'Num({})'.format(self.value)

    def __str__(self):
        return str(self.value)

    def _compare(self, other):
        return self.value < other.value

    def _add(self, other):
        self.value += other.value

    def _mul(self, other):
        if isinstance(other, NumNode):
            self.value *= other.value
        if other.__class__ in [int, float]:
            self.value *= other
        else:
            return other * self


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

    def __repr__(self):
        return 'Term({})'.format(', '.join(map(repr, self.factors)))

    def __str__(self):
        return ' + '.join(map(str, self.factors))

    def _compare(self, other):
        return len(self.factors) < len(other.factors)

    def _add(self, other):
        self.factors.extend(other.factors)

    def _mul(self, other):
        if isinstance(other, NumNode):
            for x in self.factors:
                x *= other
        return FactorNode([self, other], [])


class FactorNode(MathNode):
    order = 5

    def __init__(self, numerator: list, denominator: list, coef=(1, 1)):
        super(FactorNode, self).__init__()
        self.numerator = sorted(numerator)
        self.denominator = sorted(denominator)
        self.coef = coef

        self._update_coef()

        if coef[1] % 1 != 0:    # coef[1] is not `int`
            self.coef = coef[0] / coef[1], 1

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

    def __repr__(self):
        nu = '{}'.format(self.coef[0])
        if len(self.numerator) > 0:
            nu += ' * {}'.format(', '.join(map(repr, self.numerator)))
        if self.coef[1] == 1 and len(self.denominator) == 0:
            s = nu
        else:
            deno = '{}'.format(self.coef[1])
            if len(self.denominator) > 0:
                deno += ' * {}'.format(', '.join(map(repr, self.denominator)))
            s = '{} / {}'.format(nu, deno)
        return 'Factor({})'.format(s)

    def __str__(self):
        nu, deno = '', ''
        if len(self.numerator) > 0:
            nu = '*'.join(map(str, self.numerator))
        if len(self.denominator) > 0:
            deno = '*'.join(map(str, self.denominator))

        if nu == '':
            nu = str(self.coef[0])
        elif self.coef[0] != 1:
            nu = '{}*{}'.format(self.coef[0], nu)

        if deno == '' and self.coef[1] != 1:
            nu += ' / {}'.format(self.coef[1])
        elif deno != '':
            if self.coef[1] != 1:
                deno = '{}*{}'.format(self.coef[1], deno)
            nu += ' / {}'.format(deno)

        return '({})'.format(nu)

    def _compare(self, other):
        return self._get_order() < other._get_order()

    def _get_dim(self):
        return self.numerator, self.denominator

    def _get_order(self):
        return max([x.order for x in self.numerator]
                   + [x.order for x in self.denominator] + [0])

    def _intify(self, coef):
        a, b = coef
        if a % 1 == 0:
            a = int(a)
        if b % 1 == 0:
            b = int(b)
        return a, b

    def _update_coef(self):
        nu = [x for x in self.numerator if isinstance(x, NumNode)]
        deno = [x for x in self.denominator if isinstance(x, NumNode)]

        a, b = self.coef
        for x in nu:
            a *= x.value
        for x in deno:
            b *= x.value

        self.numerator = [x for x in self.numerator if not isinstance(x, NumNode)]
        self.denominator = [x for x in self.denominator if not isinstance(x, NumNode)]
        self.coef = self._intify((a, b))

    def _add(self, other):
        a, b = self.coef
        c, d = other.coef

        gcd = math.gcd(b, d)
        nu = (a * gcd / b) + (c * gcd / d)
        self.coef = self._intify((nu, gcd))
        return self

    def _mul(self, other):
        if isinstance(other, TermNode):
            return other * self
        if isinstance(other, FactorNode):
            return self
            # nu = self.numerator + other.numerator
            # deno = self.denominator + other.denominator
            # # TODO: simplify nu & deno
            # return FactorNode(nu, deno)
        if isinstance(other, NumNode):
            self.coef = other.value * self.coef[0], self.coef[1]
            return self
        if isinstance(other, MathNode):
            self.numerator.append(other)
            return self


class PolyNode(MathNode):
    order = 1

    def __init__(self, body, dim=1):
        super(PolyNode, self).__init__()
        self.body = body
        self.dim = dim

    def similar(self, other):
        if not isinstance(other, PolyNode):
            return False
        return other.body.similar(self.body) and other.dim == self.dim

    def __repr__(self):
        return 'Poly({}, {})'.format(repr(self.body), self.dim)

    def __str__(self):
        if isinstance(self.body, TermNode):
            return '({})^{}'.format(self.body, self.dim)
        return '{}^{}'.format(self.body, self.dim)

    def _compare(self, other):
        return self.dim > other.dim

    def _add(self, other):
        return FactorNode([self], [], (2, 1))

    def _mul(self, other):
        if other.__class__ in [TermNode, FactorNode]:
            return other * self
        if isinstance(other, NumNode):
            return FactorNode([self], [], (other.value, 1))
        if self.similar(other):
            dim = self.dim + other.dim
            return PolyNode(self.body, dim)
        if isinstance(other, MathNode):
            return FactorNode([self, other], [])


class ExpoNode(MathNode):
    order = 2

    def __init__(self, base, body):
        super(ExpoNode, self).__init__()
        self.base = base
        self.body = body

    def similar(self, other):
        if not isinstance(other, ExpoNode):
            return False
        return self == other

    def __repr__(self):
        return 'Expo({}, {})'.format(self.base, self.body)

    def __str__(self):
        base = '({})'.format(self.base) if isinstance(self.base, TermNode) else str(self.base)
        body = '({})'.format(self.body) if isinstance(self.body, TermNode) else str(self.body)
        return '{}^{}'.format(base, body)

    def _compare(self, other):
        return self.base < other.base

    def _add(self, other):
        return FactorNode([self], [], (2, 1))

    def _mul(self, other):
        if other.__class__ in [TermNode, FactorNode]:
            return other * self
        if isinstance(other, NumNode):
            return FactorNode([self], [], (other.value, 1))
        if isinstance(other, ExpoNode):
            if self.similar(other):
                self.body = TermNode([self.body, other.body])
            else:
                self.body
        if isinstance(other, MathNode):
            return FactorNode([self, other], [])


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

    def __repr__(self):
        return 'Log({}, {})'.format(self.base, self.body)

    def __str__(self):
        base = '({})'.format(self.base) if isinstance(self.base, TermNode) else str(self.base)
        # body = '({})'.format(self.body) if isinstance(self.body, TermNode) else str(self.body)
        return 'log{}_({})'.format(base, self.body)

    def _compare(self, other):
        return self.base < other.base

    def _add(self, other):
        self.body = TermNode([FactorNode([self.body, other.body], [])])

    def _mul(self, other):
        if other.__class__ in [TermNode, FactorNode]:
            return other * self
        if isinstance(other, NumNode):
            return FactorNode([self], [], (other.value, 1))
        if isinstance(other, MathNode):
            return FactorNode([self, other], [])


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

    def __repr__(self):
        func = self.func[0].upper() + self.func[1:]
        return '{}({})'.format(func, repr(self.body))

    def __str__(self):
        # body = '({})'.format(self.body) if isinstance(self.body, TermNode) else str(self.body)
        return '{}({})'.format(self.func, self.body)

    def _compare(self, other):
        func_order = {'sin': 0, 'cos': 1, 'tan': 2}
        return func_order[self.func] < func_order[other.func]

    def _add(self, other):
        return FactorNode([self], [], (2, 1))

    def _mul(self, other):
        if other.__class__ in [TermNode, FactorNode]:
            return other * self
        if isinstance(other, NumNode):
            return FactorNode([self], [], (other.value, 1))
        if isinstance(other, MathNode):
            return FactorNode([self, other], [])


class VarNode(MathNode):
    order = 1.5

    def __init__(self, name):
        super(VarNode, self).__init__()
        self.name = name

    def similar(self, other):
        if not isinstance(other, VarNode):
            return False
        return self.name == other.name

    def __repr__(self):
        return 'Var({})'.format(self.name)

    def __str__(self):
        return self.name

    def _compare(self, other):
        return self.name < other.name

    def _add(self, other):
        # ???
        pass

    def _mul(self, other):
        pass


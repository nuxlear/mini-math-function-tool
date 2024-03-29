import abc
import math
import functools


@functools.total_ordering
class MathNode(metaclass=abc.ABCMeta):
    order = None

    @abc.abstractmethod
    def similar_add(self, other) -> bool:
        pass

    @abc.abstractmethod
    def similar_mul(self, other) -> bool:
        pass

    def __lt__(self, other):
        if self.__class__ != other.__class__:
            return self.orders() < other.orders()
        return self._compare(other)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other.__dict__

    @abc.abstractmethod
    def _compare(self, other) -> bool:
        pass

    @abc.abstractmethod
    def orders(self):
        pass

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    def __add__(self, other):
        if not self.similar_add(other):
            raise ArithmeticError('adding `{}` and `{}` is not defined'.format(self, other))
        return self._add(other)

    def __mul__(self, other):
        if not self.similar_mul(other):
            raise ArithmeticError('multiplying `{}` and `{}` is not defined'.format(self, other))
        return self._mul(other)

    def __neg__(self):
        return FactorNode([self], [], (-1, 1))

    @abc.abstractmethod
    def _add(self, other) -> None:
        pass

    @abc.abstractmethod
    def _mul(self, other) -> None:
        pass


def is_negative(node: MathNode):
    if isinstance(node, FactorNode):
        return node.coef[0] / node.coef[1] < 0
    if isinstance(node, NumNode):
        return node.value < 0
    return False


class NumNode(MathNode):
    const_dict = {'pi': math.pi, 'e': math.e}

    def __init__(self, value):
        if value in self.const_dict:
            value = str(self.const_dict[value])
        self.value = float(value) if float(value) % 1 != 0 else int(value)

    def similar_add(self, other):
        return isinstance(other, NumNode)

    def similar_mul(self, other):
        return isinstance(other, NumNode)

    def __repr__(self):
        return 'Num({})'.format(self.value)

    def __str__(self):
        return str(self.value) if self.value >= 0 else '({})'.format(self.value)

    def _compare(self, other):
        return self.value < other.value

    def orders(self):
        return 7

    def _add(self, other):
        self.value += other.value

    def _mul(self, other):
        return NumNode(self.value * other.value)

    def __neg__(self):
        return NumNode(self.value * -1)


class TermNode(MathNode):

    def __init__(self, factors: list):
        super(TermNode, self).__init__()
        self.factors = sorted(factors)

    def similar_add(self, other):
        if not isinstance(other, TermNode) \
                or len(self.factors) != len(other.factors):
            return False
        ans = True
        for s, o in zip(self.factors, other.factors):
            ans = ans and s.similar_add(o)
        return ans

    def similar_mul(self, other):
        if isinstance(other, TermNode):
            for x, y in zip(sorted(self.factors), sorted(other.factors)):
                if x != y:
                    return False
            return True
        if isinstance(other, PolyNode):
            return self == other.body
        return False

    def __repr__(self):
        return 'Term({})'.format(', '.join(map(repr, self.factors)))

    def __str__(self):
        if len(self.factors) == 0:
            return '0'
        s = str(self.factors[0])
        for x in self.factors[1:]:
            if is_negative(x):
                s += ' - {}'.format(-x)
            else:
                s += ' + {}'.format(x)
        return '{}'.format(s)

    def _compare(self, other):
        return self._get_order() < other._get_order()

    def orders(self):
        return max([x.orders() for x in self.factors])

    def _get_order(self):
        k = [x.orders() for x in self.factors]
        return max(k) if len(k) > 0 else -1

    def _add(self, other):
        self.factors.extend(other.factors)

    def _mul(self, other):
        if isinstance(other, NumNode):
            for x in self.factors:
                x *= other
        return FactorNode([self, other], [])

    def __neg__(self):
        return TermNode([-f for f in self.factors])


class FactorNode(MathNode):

    def __init__(self, numerator: list, denominator: list=[], coef=(1, 1)):
        super(FactorNode, self).__init__()
        self.numerator = sorted(numerator)
        self.denominator = sorted(denominator)
        self.coef = coef

        self.update_coef()

    def similar_add(self, other):
        if not isinstance(other, FactorNode):
            return False
        nu, deno = self._get_dim()
        fnu, fdeno = other._get_dim()
        if len(nu) != len(fnu) or len(deno) != len(fdeno):
            return False
        ans = True
        for x in nu:
            ans = ans and x in fnu
        for x in fnu:
            ans = ans and x in nu
        for x in deno:
            ans = ans and x in fdeno
        for x in fdeno:
            ans = ans and x in deno
        return ans

    def similar_mul(self, other):
        if isinstance(other, FactorNode):
            return True
        return False

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
        s = ''
        if self.coef[0] / self.coef[1] < 0:
            s += '-'
        c_nu = '{}'.format(abs(self.coef[0]))
        c_deno = '{}'.format(abs(self.coef[1]))

        def _pack_term(node):
            if isinstance(node, TermNode):
                return '({})'.format(node)
            return str(node)

        nu = '{}'.format('*'.join(map(_pack_term, self.numerator)))
        deno = '{}'.format('*'.join(map(_pack_term, self.denominator)))

        if deno == '':
            if c_deno != '1':
                s += '{} / {}'.format(c_nu, c_deno)
            else:
                if c_nu != '1' or nu == '':
                    s += '{}'.format(c_nu)

            if nu != '':
                if c_nu != '1':
                    s += '*'
                s += '{}'.format(nu)
        else:
            if c_nu != '1' or nu == '':
                _nu = c_nu
                if nu != '':
                    _nu += '*{}'.format(nu)
                nu = _nu
            if c_deno != '1':
                deno = '{}*{}'.format(c_deno, deno)
            if len(self.denominator) > 1 \
                    or c_deno != '1' and len(self.denominator) > 0:
                deno = '({})'.format(deno)
            s += '{}/{}'.format(nu, deno)
        return s

    def _compare(self, other):
        return self._get_order() < other._get_order()

    def orders(self):
        k = [x.orders() for x in self.numerator] + [x.orders() for x in self.denominator]
        return max(k) if len(k) > 0 else 7

    def _get_dim(self):
        return sorted(self.numerator), sorted(self.denominator)

    def _get_order(self):
        k = [x.orders() for x in self.numerator] + [x.orders() for x in self.denominator]
        return max(k) if len(k) > 0 else 7

    def _intify(self, coef):
        a, b = coef
        if a % 1 == 0:
            a = int(a)
        if b % 1 == 0:
            b = int(b)
        return a, b

    def update_coef(self):
        nu = [x for x in self.numerator if isinstance(x, NumNode)]
        deno = [x for x in self.denominator if isinstance(x, NumNode)]

        a, b = self.coef
        for x in nu:
            a *= x.value
        for x in deno:
            b *= x.value

        self.numerator = [x for x in self.numerator if not isinstance(x, NumNode)]
        self.denominator = [x for x in self.denominator if not isinstance(x, NumNode)]

        if self.coef[0] % 1 != 0 and self.coef[1] % 1 != 0:     # (x.xx / x.xx)
            self.coef = self.coef[0] / self.coef[1], 1
        self.coef = self._intify((a, b))

    def inverse(self):
        a, b = self.coef
        return FactorNode(self.denominator, self.numerator, (b, a))

    def _add(self, other):
        a, b = self.coef
        c, d = other.coef

        gcd = math.gcd(b, d)
        nu = (a * gcd / b) + (c * gcd / d)
        self.coef = self._intify((nu, gcd))
        return self

    def _mul(self, other):
        if isinstance(other, FactorNode):
            nu = self.numerator + other.numerator
            deno = self.denominator + other.denominator
            coef = self.coef[0] * other.coef[0], self.coef[1] * other.coef[1]

            return FactorNode(nu, deno, coef)

    def __neg__(self):
        return FactorNode(self.numerator, self.denominator,
                          (-self.coef[0], self.coef[1]))


class PolyNode(MathNode):

    def __init__(self, body, dim=1):
        super(PolyNode, self).__init__()
        self.body = body
        self.dim = float(dim) if float(dim) % 1 != 0 else int(dim)

    def similar_add(self, other):
        if not isinstance(other, PolyNode):
            return False
        return other.body.similar_add(self.body) and other.dim == self.dim

    def similar_mul(self, other):
        if isinstance(other, PolyNode):
            return other.body == self.body
        if isinstance(other, ExpoNode):
            return other.base.similar_add(self.body)
        return other == self.body

    def __repr__(self):
        return 'Poly({}, {})'.format(repr(self.body), self.dim)

    def __str__(self):
        body = str(self.body)
        if self.body.__class__ not in [VarNode, NumNode]:
            body = '({})'.format(body)
        return '{}^{}'.format(body, self.dim)

    def _compare(self, other):
        return self.dim > other.dim

    def orders(self):
        return 1

    def _add(self, other):
        return FactorNode([self], [], (2, 1))

    def _mul(self, other):
        if isinstance(other, PolyNode):
            return PolyNode(self.body, self.dim + other.dim)
        if isinstance(other, ExpoNode):
            if other.body.similar_add(self.dim):
                return ExpoNode(self.body, self.dim + other.body)
            if isinstance(other.body, TermNode):
                other.body.factors.append(FactorNode([NumNode(self.dim)], []))
                return ExpoNode(self.body, other.body)
            return ExpoNode(self.body, TermNode([
                FactorNode([NumNode(self.dim)], []), FactorNode([other.body], [])]))
        return PolyNode(self.body, self.dim + 1)


class ExpoNode(MathNode):

    def __init__(self, base, body):
        super(ExpoNode, self).__init__()
        self.base = base
        self.body = body

    def similar_add(self, other):
        if not isinstance(other, ExpoNode):
            return False
        return self == other

    def similar_mul(self, other):
        if isinstance(other, ExpoNode):
            return other.base.similar_add(self.base)
        if isinstance(other, PolyNode):
            return other.body == self.base
        return other == self.base

    def __repr__(self):
        return 'Expo({}, {})'.format(repr(self.base), repr(self.body))

    def __str__(self):
        base = str(self.base)
        body = str(self.body)
        if self.base.__class__ not in [VarNode, NumNode]:
            base = '({})'.format(base)
        if self.body.__class__ not in [VarNode, NumNode]:
            body = '({})'.format(body)
        return '{}^{}'.format(base, body)

    def _compare(self, other):
        return self.base < other.base

    def orders(self):
        return 2

    def _add(self, other):
        return FactorNode([self], [], (2, 1))

    def _mul(self, other):
        if isinstance(other, PolyNode):
            return ExpoNode(self.base, TermNode([
                FactorNode([self.body], []), FactorNode([NumNode(other.dim)], [])]))
        if isinstance(other, ExpoNode):
            if self.body.similar_add(other.body):
                return ExpoNode(self.base, self.body + other.body)
            if isinstance(self.body, TermNode):
                self.body.factors.append(other.body)
                return ExpoNode(self.base, self.body)
            if isinstance(other.body, TermNode):
                other.body.factors.append(self.body)
                return ExpoNode(self.base, other.body)
            return ExpoNode(self.base, TermNode([
                FactorNode([self.body], []), FactorNode([other.body], [])]))

        return ExpoNode(self.base, TermNode([
                FactorNode([self.body], []), FactorNode([], [])]))


class LogNode(MathNode):

    def __init__(self, base, body):
        if isinstance(base, NumNode) and (base.value <= 0 or base.value == 1):
            raise ValueError('Invalid base for logarithm: {}'.format(base.value))

        super(LogNode, self).__init__()
        self.base = base
        self.body = body

    def similar_add(self, other):
        if not isinstance(other, LogNode):
            return False
        return self.base == other.base

    def similar_mul(self, other):
        return self == other

    def __repr__(self):
        return 'Log({}, {})'.format(repr(self.base), repr(self.body))

    def __str__(self):
        base = '({})'.format(self.base) if self.base.__class__ not in [VarNode, NumNode] else str(self.base)
        # body = '({})'.format(self.body) if isinstance(self.body, TermNode) else str(self.body)
        return 'log{}_({})'.format(base, self.body)

    def _compare(self, other):
        return self.base < other.base

    def orders(self):
        return 4

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

    def __init__(self, func, body):
        super(TriNode, self).__init__()
        self.func = func
        self.body = body

    def similar_add(self, other):
        if not isinstance(other, TriNode):
            return False
        return self.func == other.func

    def similar_mul(self, other):
        return self == other

    def __repr__(self):
        func = self.func[0].upper() + self.func[1:]
        return '{}({})'.format(func, repr(self.body))

    def __str__(self):
        return '{}({})'.format(self.func, self.body)

    def _compare(self, other):
        func_order = {'sin': 0, 'cos': 1, 'tan': 2}
        return func_order[self.func] < func_order[other.func]

    def orders(self):
        return 3

    def _add(self, other):
        return FactorNode([self], [], (2, 1))

    def _mul(self, other):
        return PolyNode(self, 2)


class VarNode(MathNode):

    def __init__(self, name):
        super(VarNode, self).__init__()
        self.name = name

    def similar_add(self, other):
        if not isinstance(other, VarNode):
            return False
        return self.name == other.name

    def similar_mul(self, other):
        if isinstance(other, PolyNode):
            return self.similar_add(other.body)
        if isinstance(other, VarNode):
            return self.similar_add(other)

    def __repr__(self):
        return 'Var({})'.format(self.name)

    def __str__(self):
        return self.name

    def _compare(self, other):
        return self.name < other.name

    def orders(self):
        return 1.5

    def _add(self, other):
        return FactorNode([self], [], (2, 1))

    def _mul(self, other):
        if isinstance(other, VarNode):
            return PolyNode(self, 2)
        return PolyNode(other.body, other.dim + 1)


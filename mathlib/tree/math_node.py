import mathlib
from mathlib import abc, Union, operator


class MathNode(metaclass=abc.ABCMeta):
    """ Make immutable """

    # canonicalization

    @abc.abstractmethod
    def simplify(self):
        pass

    @abc.abstractmethod
    def merge_similar(self):
        pass

    @abc.abstractmethod
    def is_negative(self) -> bool:
        pass

    @abc.abstractmethod
    def is_zero(self) -> bool:
        pass

    def similar_add(self, other) -> bool:
        """ Return whether `self` and `other` get merged by addition. """
        if not isinstance(other, MathNode):
            return False
        return self.get_add_dim() == other.get_add_dim()

    def similar_mul(self, other) -> bool:
        """ Return whether `self` and `other` get merged by multiplication. """
        if not isinstance(other, MathNode):
            return False
        return self.get_mul_dim() == other.get_mul_dim()

    @abc.abstractmethod
    def get_add_dim(self):
        pass

    @abc.abstractmethod
    def get_mul_dim(self):
        pass

    # mathmatical

    @abc.abstractmethod
    def eval(self, **kwargs):
        pass

    @abc.abstractmethod
    def derivative(self, var):
        pass

    @abc.abstractmethod
    def exclusion(self) -> list:
        pass

    # comparator

    def __lt__(self, other):
        if self.get_order() == other.get_order():
            return self.get_sub_order() < other.get_sub_order()
        return self.get_order() < other.get_order()

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
               self.__dict__ == other.__dict__

    @abc.abstractmethod
    def get_order(self) -> Union[int, float]:
        pass

    @abc.abstractmethod
    def get_sub_order(self) -> Union[int, float]:
        pass

    # print

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__[:-4], self.get_repr_content())

    @abc.abstractmethod
    def get_repr_content(self) -> str:
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def latex(self) -> str:
        pass

    # arithmetic

    @abc.abstractmethod
    def __neg__(self):
        pass

    @abc.abstractmethod
    def __add__(self, other):
        pass

    @abc.abstractmethod
    def __sub__(self, other):
        pass

    @abc.abstractmethod
    def __mul__(self, other):
        pass

    @abc.abstractmethod
    def __truediv__(self, other):
        pass


# Structural Nodes

class StructuralNode(MathNode, metaclass=abc.ABCMeta):

    @staticmethod
    def merge_op(nodes: Union[list, tuple], op) -> list:
        nodes = [x for x in nodes if x is not None]
        merged = []
        for x in nodes:
            q = []
            for i, s in enumerate(merged):
                if op == operator.add and s.similar_add(x) or \
                        op == operator.mul and s.similar_mul(x):
                    q.append(op(s, x))
                    q.extend(merged[i+1:])
                    break
                else:
                    q.append(s)
            else:
                q.append(x)
            merged = q
        return merged

    def latex(self) -> str:
        return str(self)


class TermNode(StructuralNode):

    def __init__(self, factors: Union[tuple, list] = tuple()):
        self.factors = tuple(sorted(factors))

    def simplify(self):
        factors = [x.simplify() for x in self.factors if not isinstance(x, TermNode)]
        n = TermNode(factors)
        for x in self.factors:
            if isinstance(x, TermNode):
                n += x

        if len(n.factors) == 0:
            return NumNode(0)
        if len(n.factors) == 1:
            return n.factors[0]
        return n

    def merge_similar(self):
        factors = [x.merge_similar() for x in self.factors]
        merged = StructuralNode.merge_op(factors, operator.add)
        merged = [x for x in merged if not x.is_zero()]
        return TermNode(merged)

    def is_negative(self) -> bool:
        return False

    def is_zero(self) -> bool:
        return len(self.factors) == 0

    def get_add_dim(self):
        return TermNode()

    def get_mul_dim(self):
        return self

    def eval(self, **kwargs):
        result = 0
        for x in self.factors:
            result += x.eval(**kwargs)
        return result

    def derivative(self, var):
        factors = [x.derivative(var) for x in self.factors]
        return TermNode(factors)

    def exclusion(self) -> list:
        ex = []
        for x in self.factors:
            ex.extend(x.exclusion())
        return ex

    def get_order(self) -> Union[int, float]:
        return max([x.get_order() for x in self.factors] + [0])

    def get_sub_order(self) -> Union[int, float]:
        return max([x.get_sub_order() for x in self.factors] + [0])

    def get_repr_content(self) -> str:
        return '[{}]'.format(', '.join(map(repr, self.factors)))

    def __str__(self):
        if len(self.factors) == 0:
            return '0'
        s = str(self.factors[0])
        for x in self.factors[1:]:
            if x.is_negative():
                s += ' - {}'.format(-x)
            else:
                s += ' + {}'.format(x)
        return '{}'.format(s)

    def __neg__(self):
        factors = [-x for x in self.factors]
        return TermNode(factors)

    def __add__(self, other):
        if isinstance(other, TermNode):
            return TermNode(self.factors + other.factors)

        # factors = [x.simplify() for x in self.factors if not x.similar_add(other)]
        # if len(factors) != len(self.factors):
        #     similars = [x for x in self.factors if x not in factors]
        #     for x in similars:
        #         other += x
        factors = list(self.factors)
        return TermNode(factors + [other])

    def __sub__(self, other):
        if isinstance(other, TermNode):
            return self + (-other)
        return TermNode(self.factors + (-other,))

    def __mul__(self, other):
        return (FactorNode() * self) * other

    def __truediv__(self, other):
        if self == other:
            return NumNode(1)
        return (FactorNode() * self) / other


class FactorNode(StructuralNode):

    @staticmethod
    def add_coefs(this, other):
        (a, b), (c, d) = this, other
        gcd = mathlib.math.gcd(b, d)
        nu = a * (d / gcd) + c * (b / gcd)
        return nu, gcd

    @staticmethod
    def relocate(numerator, denominator):
        nu, deno = [], []
        for x in numerator:
            if isinstance(x, ExpoNode) and x.dim.is_negative():
                deno.append(ExpoNode(x.body, -x.dim))
            else:
                nu.append(x)
        for x in denominator:
            if isinstance(x, ExpoNode) and x.dim.is_negative():
                nu.append(ExpoNode(x.body, -x.dim))
            else:
                deno.append(x)
        return nu, deno

    @staticmethod
    def abbreviate(numerator, denominator):
        nu, deno = [], denominator
        for x in numerator:
            used = []
            for y in deno:
                if x.similar_mul(y):
                    nu.append(x / y)
                    used.append(y)
                    break
            else:
                nu.append(x)
            deno = [x for x in deno if x not in used]
        return FactorNode.relocate(nu, deno)

    def __init__(self, numerator: Union[tuple, list] = tuple(),
                 denominator: Union[tuple, list] = tuple(),
                 coef: tuple = (1, 1)):

        def _separate_nodes(_nodes, _coef=1):
            coef_nodes, nodes = [], []
            for x in _nodes:
                if isinstance(x, NumNode):
                    if NumNode.is_number(x.value):
                        _coef *= x.value
                    else:
                        coef_nodes.append(x)
                else:
                    nodes.append(x)
            return _coef, coef_nodes, nodes

        a, c_nu, nu = _separate_nodes(numerator, coef[0])
        b, c_deno, deno = _separate_nodes(denominator, coef[1])

        if not NumNode.is_int(a) or not NumNode.is_int(b):
            a, b = a / b, 1
        if NumNode.is_int(a):
            a = int(a)
        coef = a, b

        self.numerator = tuple(sorted(c_nu) + sorted(nu))
        self.denominator = tuple(sorted(c_deno) + sorted(deno))
        self.coef = tuple(coef)

    def get_coef(self):
        return self.coef[0] / self.coef[1]

    def simplify(self):
        if self.get_coef() == 0:
            return NumNode(0)

        n = FactorNode([x.simplify() for x in self.numerator if not isinstance(x, FactorNode)],
                       [x.simplify() for x in self.denominator if not isinstance(x, FactorNode)],
                       self.coef)
        for x in self.numerator:
            if isinstance(x, FactorNode):
                n *= x
        for x in self.denominator:
            if isinstance(x, FactorNode):
                n /= x

        nu, deno = n.numerator, n.denominator

        nu, deno = FactorNode.relocate(nu, deno)
        nu, deno = FactorNode.abbreviate(nu, deno)

        nu = [x.simplify() for x in nu]
        deno = [x.simplify() for x in deno]

        n = FactorNode(nu, deno, n.coef)

        if len(n.denominator) == 0:
            # only numerator & coefficient
            if len(n.numerator) == 0:
                return NumNode(n.get_coef())
            if len(n.numerator) == 1 and n.get_coef() == 1:
                return n.numerator[0]
        return n

    def merge_similar(self):
        nu = [x.merge_similar() for x in self.numerator]
        deno = [x.merge_similar() for x in self.denominator]

        nu = StructuralNode.merge_op(nu, operator.mul)
        deno = StructuralNode.merge_op(deno, operator.mul)

        nu = [x for x in nu if not x.is_zero()]
        deno = [x for x in deno if not x.is_zero()]
        return FactorNode(nu, deno, self.coef)

    def is_negative(self) -> bool:
        return self.get_coef() < 0

    def is_zero(self) -> bool:
        z = self.get_coef() == 0
        for x in self.numerator:
            z &= x.is_zero()
        return z

    def get_add_dim(self):
        # need to remove numbers
        return FactorNode(self.numerator, self.denominator).simplify()

    def get_mul_dim(self):
        return FactorNode()

    def eval(self, **kwargs):
        nu, deno = self.coef
        for x in self.numerator:
            nu *= x.eval(**kwargs)
        for x in self.denominator:
            deno *= x.eval(**kwargs)
        if deno == 0:
            return mathlib.math.nan
        return nu / deno

    def derivative(self, var):
        if len(self.numerator) == 0 and len(self.denominator) == 1:
            d = self.denominator[0]
            return FactorNode([d.derivative(var), NumNode(-1)], [ExpoNode(d, NumNode(2))], self.coef)

        c_nu = [x for x in self.numerator if var not in str(x)]
        c_deno = [x for x in self.denominator if var not in str(x)]
        c = FactorNode(c_nu, c_deno, self.coef)

        nu = [x for x in self.numerator if x not in c_nu]
        deno = [FactorNode([], [x]) for x in self.denominator if x not in c_deno]

        targets = nu + deno
        factors = []
        for t in targets:
            others = [t.derivative(var)] + [x for x in targets if x != t]
            factors.append(FactorNode(others) * c)
        return TermNode(factors)

    def exclusion(self) -> list:
        ex = []
        for x in self.denominator:
            ex.append([(x, operator.eq, 0)])
        for x in self.numerator + self.denominator:
            ex.extend(x.exclusion())
        return ex

    def get_order(self) -> Union[int, float]:
        return max([x.get_order() for x in self.numerator + self.denominator] + [0])

    def get_sub_order(self) -> Union[int, float]:
        return max([x.get_sub_order() for x in self.numerator + self.denominator] + [0])

    def get_repr_content(self) -> str:
        nu = '{}'.format(self.coef[0])
        if len(self.numerator) > 0:
            nu += ' * [{}]'.format(', '.join(map(repr, self.numerator)))
        if self.coef[1] == 1 and len(self.denominator) == 0:
            s = nu
        else:
            deno = '{}'.format(self.coef[1])
            if len(self.denominator) > 0:
                deno += ' * [{}]'.format(', '.join(map(repr, self.denominator)))
            s = '{} / {}'.format(nu, deno)
        return s

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
                    or c_deno != '1' and len(self.denominator) > 0\
                    or '*' in deno:
                deno = '({})'.format(deno)
            s += '{}/{}'.format(nu, deno)
        return s

    def __neg__(self):
        return FactorNode(self.numerator, self.denominator,
                          (-self.coef[0], self.coef[1])).simplify()

    def __add__(self, other):
        if self.similar_add(other):
            if not isinstance(other, FactorNode):
                other = FactorNode([other])
            return FactorNode(self.numerator, self.denominator,
                              FactorNode.add_coefs(self.coef, other.coef))
        return (TermNode() + self) + other

    def __sub__(self, other):
        if self.similar_add(other):
            if not isinstance(other, FactorNode):
                other = FactorNode([other])
            other *= -1
            return FactorNode(self.numerator, self.denominator,
                              FactorNode.add_coefs(self.coef, other.coef))
        return (TermNode() + self) - other

    def __mul__(self, other):
        if isinstance(other, FactorNode):
            (n, d), (_n, _d) = self.coef, other.coef
            return FactorNode(self.numerator + other.numerator,
                              self.denominator + other.denominator,
                              (n * _n, d * _d))
        if isinstance(other, ExpoNode):
            if other.dim.is_negative():
                return self.__truediv__(ExpoNode(other.body, -other.dim))

        # nu = [x.simplify() for x in self.numerator if not x.similar_mul(other)]
        # deno = [x.simplify() for x in self.denominator if not x.similar_mul(other)]
        # if len(nu) != len(self.numerator):
        #     similars = [x for x in self.numerator if x not in nu]
        #     for x in similars:
        #         other *= x
        # if len(deno) != len(self.denominator):
        #     similars = [x for x in self.denominator if x not in deno]
        #     for x in similars:
        #         other /= x
        nu = list(self.numerator)
        deno = list(self.denominator)

        return FactorNode(nu + [other.simplify()], deno, self.coef)

    def __truediv__(self, other):
        if isinstance(other, FactorNode):
            (n, d), (_n, _d) = self.coef, other.coef
            return FactorNode(self.numerator + other.denominator,
                              self.denominator + other.numerator,
                              (n * _d, d * _n))
        if isinstance(other, ExpoNode):
            if other.dim.is_negative():
                return self.__mul__(ExpoNode(other.body, -other.dim))

        # nu = [x for x in self.numerator if not x.similar_mul(other)]
        # deno = [x for x in self.denominator if not x.similar_mul(other)]
        # if len(nu) != len(self.numerator):
        #     similars = [x for x in self.numerator if x not in nu]
        #     for x in similars:
        #         other /= x
        # if len(deno) != len(self.denominator):
        #     similars = [x for x in self.denominator if x not in deno]
        #     for x in similars:
        #         other *= x
        nu = list(self.numerator)
        deno = list(self.denominator)

        return FactorNode(nu, deno + [other.simplify()], self.coef)


# Content Nodes

class ContentNode(MathNode, metaclass=abc.ABCMeta):

    def __neg__(self):
        # return FactorNode([self], coef=(-1, 1))
        return self * -1

    def __add__(self, other):
        if other.__class__ in [int, float]:
            return TermNode([self, NumNode(other)])
        # if self == -other or -self == other:
        #     return NumNode(0)
        if self.similar_add(other):
            if self == other:
                return FactorNode([self], coef=(2, 1))
            return FactorNode([self]) + other
        return (TermNode() + self) + other

    def __sub__(self, other):
        if other.__class__ in [int, float]:
            return TermNode([self, NumNode(-other)])
        if self.similar_add(other):
            if self == other:
                return NumNode(0)
            return FactorNode([self]) - other
        return (TermNode() + self) - other

    def __mul__(self, other):
        if other.__class__ in [int, float]:
            return FactorNode([self], coef=(other, 1))
        if self.similar_mul(other):
            if self == other:
                return ExpoNode(self, NumNode(2))
            return ExpoNode(self, NumNode(1)) * other
        return (FactorNode() * self) * other

    def __truediv__(self, other):
        if other.__class__ in [int, float]:
            return FactorNode([self], coef=(1, other))
        if self.similar_mul(other):
            if self == other:
                return NumNode(1)
            return ExpoNode(self, NumNode(-1)) * other
        return (FactorNode() * self) / other


# Elementary Nodes

class ElementaryNode(ContentNode, metaclass=abc.ABCMeta):

    def __init__(self, body: MathNode):
        self.body = body

    def is_negative(self) -> bool:
        return False


class ExpoNode(ElementaryNode):

    @staticmethod
    def check_int(x, y):
        return NumNode.is_int(x) == y

    def __init__(self, body: MathNode, dim: MathNode):
        super(ExpoNode, self).__init__(body)
        self.dim = dim

    def simplify(self):
        body = self.body.simplify()
        dim = self.dim.simplify()

        if isinstance(body, ExpoNode):
            return ExpoNode(body.body, body.dim * dim)

        if isinstance(dim, NumNode) and NumNode.is_int(dim.value):
            # Polynomial
            if isinstance(body, NumNode):
                return NumNode(body.value ** dim.value)
            if dim.value == 1:
                return self.body
            if dim.value == 0:
                return NumNode(1)
            if dim.value < 0:
                return FactorNode([], [ExpoNode(body, -dim)])

        if isinstance(dim, LogNode):
            # e^lnx
            if body == dim.base:
                return dim.body

        return ExpoNode(body, dim)

    def merge_similar(self):
        return ExpoNode(self.body.merge_similar(), self.dim.merge_similar())

    def is_zero(self) -> bool:
        return self.body.is_zero()

    def get_add_dim(self):
        return self

    def get_mul_dim(self):
        return self.body

    def eval(self, **kwargs):
        return pow(self.body.eval(**kwargs), self.dim.eval(**kwargs))

    def derivative(self, var):
        if var not in str(self):
            return NumNode(0)
        if var not in str(self.body):
            # form of a^f(x)
            return FactorNode([self, LogNode(NumNode('e'), self.body), self.dim.derivative(var)])
        if var not in str(self.dim):
            # form of f(x)^a
            return FactorNode([self.dim, ExpoNode(self.body, self.dim - NumNode(1)), self.body.derivative(var)])
        return ExpoNode(NumNode('e'),
                        FactorNode([LogNode(NumNode('e'), self.body), self.dim])).derivative(var)

    def exclusion(self) -> list:
        return [[(self.body, operator.lt, 0),
                 (self.dim, ExpoNode.check_int, False)]]

    def get_order(self) -> Union[int, float]:
        if isinstance(self.dim, NumNode):
            return 1
        return 3

    def get_sub_order(self) -> Union[int, float]:
        if isinstance(self.dim, NumNode):
            return self.body.get_order()
        return self.dim.get_order()

    def get_repr_content(self) -> str:
        return '{}, {}'.format(repr(self.body), repr(self.dim))

    def __str__(self):
        body = str(self.body)
        dim = str(self.dim)
        if self.body.__class__ not in [VarNode, NumNode]:
            body = '({})'.format(body)
        if self.dim.__class__ not in [VarNode, NumNode]:
            dim = '({})'.format(dim)
        return '{}^{}'.format(body, dim)

    def latex(self) -> str:
        pass
    
    def __mul__(self, other):
        if self.similar_mul(other):
            if isinstance(other, ExpoNode):
                return ExpoNode(self.body, self.dim + other.dim)
            if isinstance(other, VarNode):
                return ExpoNode(self.body, self.dim + NumNode(1))
        return super(ExpoNode, self).__mul__(other)

    def __truediv__(self, other):
        if self.similar_mul(other):
            if isinstance(other, ExpoNode):
                return ExpoNode(self.body, self.dim - other.dim)
            if isinstance(other, VarNode):
                return ExpoNode(self.body, self.dim - NumNode(1))
        return super(ExpoNode, self).__truediv__(other)


class LogNode(ElementaryNode):

    def __init__(self, base: MathNode, body: MathNode):
        super(LogNode, self).__init__(body)
        self.base = base

    def simplify(self):
        base = self.base.simplify()
        body = self.body.simplify()

        if body == base:
            return NumNode(1)
        if body == NumNode(1):
            return NumNode(0)
        if isinstance(body, ExpoNode):
            # ln(e^x)
            if base == body.body:
                return body.dim
        return LogNode(base, body)

    def merge_similar(self):
        return LogNode(self.base.merge_similar(), self.body.merge_similar())

    def is_zero(self) -> bool:
        return self.body == NumNode(1)

    def get_add_dim(self):
        return LogNode(self.base, NumNode(1))

    def get_mul_dim(self):
        return self

    def eval(self, **kwargs):
        return mathlib.math.log(self.body.eval(**kwargs), self.base.eval(**kwargs))

    def derivative(self, var):
        if var not in str(self.base):
            # form of log(a)_f(x)
            return FactorNode([self.body.derivative(var)],
                              [LogNode(NumNode('e'), self.base), self.body])
        return FactorNode([LogNode(NumNode('e'), self.body)],
                          [LogNode(NumNode('e'), self.base)]).derivative(var)

    def exclusion(self) -> list:
        return [[(self.base, operator.le, 0)],
                [(self.base, operator.eq, 1)],
                [(self.body, operator.le, 0)]]

    def get_order(self) -> Union[int, float]:
        return 5

    def get_sub_order(self) -> Union[int, float]:
        return self.body.get_order()

    def get_repr_content(self) -> str:
        return '{}, {}'.format(repr(self.base), repr(self.body))

    def __str__(self):
        return 'log({})_({})'.format(self.base, self.body)

    def latex(self) -> str:
        pass

    def __add__(self, other):
        if self.similar_add(other):
            return LogNode(self.base, self.body * other.body)
        return super(LogNode, self).__add__(other)

    def __sub__(self, other):
        if self.similar_add(other):
            return LogNode(self.base, self.body / other.body)
        return super(LogNode, self).__sub__(other)


class TriNode(ElementaryNode):

    func_dict = {'sin': mathlib.math.sin,
                 'cos': mathlib.math.cos,
                 'tan': mathlib.math.tan}

    @staticmethod
    def mod_pi_2(value):
        return value % (mathlib.math.pi / 2)

    @staticmethod
    def check_mod(x, y):
        return TriNode.mod_pi_2(x) == y

    def __init__(self, func: str, body: MathNode):
        super(TriNode, self).__init__(body)
        self.func = func

    def simplify(self):
        return TriNode(self.func, self.body.simplify())

    def merge_similar(self):
        return TriNode(self.func, self.body.merge_similar())

    def is_zero(self) -> bool:
        if not isinstance(self.body, NumNode):
            return False
        val = self.body.value
        if self.func == 'cos':
            val -= mathlib.math.pi

        return val % mathlib.math.pi == 0

    def get_add_dim(self):
        return self

    def get_mul_dim(self):
        return self

    def eval(self, **kwargs):
        return self.func_dict[self.func](self.body.eval(**kwargs))

    def derivative(self, var):
        if self.func == 'sin':
            return FactorNode([TriNode('cos', self.body), self.body.derivative(var)])
        if self.func == 'cos':
            return FactorNode([TriNode('sin', self.body), self.body.derivative(var)],
                              coef=(-1, 1))
        if self.func == 'tan':
            return FactorNode([self.body.derivative(var)],
                              [ExpoNode(TriNode('cos', self.body), NumNode(2))])

    def exclusion(self) -> list:
        if self.func == 'tan':
            return [[(self.body, TriNode.check_mod, 0)]]
        return []

    def get_order(self) -> Union[int, float]:
        return 4

    def get_sub_order(self) -> Union[int, float]:
        return self.body.get_sub_order()

    def __repr__(self):
        return '{}({})'.format(self.func[0].upper() + self.func[1:], self.get_repr_content())

    def get_repr_content(self) -> str:
        return repr(self.body)

    def __str__(self):
        return '{}({})'.format(self.func, self.body)

    def latex(self) -> str:
        pass


# Atomic Nodes

class AtomicNode(ContentNode, metaclass=abc.ABCMeta):

    def __init__(self, value):
        self.value = value

    def simplify(self):
        return self

    def merge_similar(self):
        return self

    def derivative(self, var):
        if var not in ['e', 'pi'] and var == self.value:
            return NumNode(1)
        return NumNode(0)

    def exclusion(self) -> list:
        return []

    def get_repr_content(self) -> str:
        return self.value

    def __str__(self):
        return '{}'.format(self.value)

    def latex(self) -> str:
        return str(self)


class VarNode(AtomicNode):

    def is_negative(self) -> bool:
        return False

    def is_zero(self) -> bool:
        return False

    def get_add_dim(self):
        return self

    def get_mul_dim(self):
        return self.get_add_dim()

    def get_order(self) -> Union[int, float]:
        return 2

    def get_sub_order(self) -> Union[int, float]:
        return ord(self.value)

    def eval(self, **kwargs):
        if self.value in kwargs:
            return kwargs[self.value]
        raise ArithmeticError('undefined variable: {}'.format(self.value))

    # def __add__(self, other):
    #     if self.similar_add(other):
    #         # # TODO: check similarity | identical
    #         # # if isinstance(other, VarNode):
    #         # return self * 2
    #         return FactorNode([self]) + other
    #     return super(VarNode, self).__add__(other)
    #
    # def __sub__(self, other):
    #     if self.similar_add(other):
    #         # return NumNode(0)
    #         return FactorNode([self]) - other
    #     return super(VarNode, self).__sub__(other)
    #
    # def __mul__(self, other):
    #     if self.similar_mul(other):
    #         return ExpoNode(self, NumNode(1)) * other
    #     return super(VarNode, self).__mul__(other)
    #
    # def __truediv__(self, other):
    #     if self.similar_mul(other):
    #         return ExpoNode(self, NumNode(-1)) * other
    #     return super(VarNode, self).__truediv__(other)


class NumNode(AtomicNode):

    @staticmethod
    def is_int(value):
        return isinstance(value, int) or \
               isinstance(value, float) and value % 1 == 0

    @staticmethod
    def is_number(value) -> bool:
        return value.__class__ in [float, int]

    @staticmethod
    def is_constant(value) -> bool:
        return value in ['e', 'pi']

    @staticmethod
    def is_valid_num(value) -> bool:
        return NumNode.is_number(value) or NumNode.is_constant(value)

    def __init__(self, value):
        if not NumNode.is_valid_num(value):
            raise ValueError('invalid number for NumNode: {}'.format(value))
        if NumNode.is_int(value):
            value = int(value)
        super(NumNode, self).__init__(value)

    def eval(self, **kwargs):
        val_dict = {'e': mathlib.math.e, 'pi': mathlib.math.pi}
        if self.value in val_dict.keys():
            return val_dict[self.value]
        return self.value

    def is_negative(self) -> bool:
        return self.is_number(self.value) and self.value < 0

    def is_zero(self) -> bool:
        return self.value == 0

    def get_add_dim(self):
        return self if self.is_constant(self.value) else NumNode(1)

    def get_mul_dim(self):
        return self.get_add_dim()

    def get_order(self) -> Union[int, float]:
        return 6

    def get_sub_order(self) -> Union[int, float]:
        return abs(self.eval())

    def latex(self) -> str:
        if self.value == 'pi':
            return '\\pi'
        return str(self.value)

    def __neg__(self):
        return NumNode(-1) * self

    def __add__(self, other):
        if self.similar_add(other):
            if self == other:
                return FactorNode([self], coef=(2, 1))
            return NumNode(self.value + other.value)
        return super(NumNode, self).__add__(other)

    def __sub__(self, other):
        if self.similar_add(other):
            if self == other:
                return NumNode(0)
            return NumNode(self.value - other.value)
        return super(NumNode, self).__sub__(other)

    def __mul__(self, other):
        if self.similar_mul(other):
            return NumNode(self.value * other.value)
        return super(NumNode, self).__mul__(other)

    def __truediv__(self, other):
        if self.similar_mul(other):
            return NumNode(self.value / other.value)
        return super(NumNode, self).__truediv__(other)


import mathlib
from mathlib import abc, Union, operator


class MathNode(metaclass=abc.ABCMeta):
    """ Make immutable """

    # canonicalization

    @abc.abstractmethod
    def simplify(self):
        pass

    @abc.abstractmethod
    def is_negative(self) -> bool:
        pass

    def similar_add(self, other) -> bool:
        """ Return whether `self` and `other` get merged by addition. """
        return self.get_add_dim() == other.get_add_dim()

    def similar_mul(self, other) -> bool:
        """ Return whether `self` and `other` get merged by multiplication. """
        return self.get_mul_dim() == other.get_mul_dim()

    @abc.abstractmethod
    def get_add_dim(self):
        pass

    @abc.abstractmethod
    def get_mul_dim(self):
        pass

    # mathmatical

    # @abc.abstractmethod
    def derivative(self):
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

    def latex(self) -> str:
        return str(self)


class TermNode(StructuralNode):

    def __init__(self, factors: Union[tuple, list] = tuple()):
        self.factors = tuple(sorted(factors))

    def simplify(self):
        if len(self.factors) == 0:
            return NumNode(0)
        if len(self.factors) == 1:
            return self.factors[0]
        return self

    def is_negative(self) -> bool:
        return False

    def get_add_dim(self):
        return TermNode()

    def get_mul_dim(self):
        return self

    def exclusion(self) -> list:
        ex = []
        for x in self.factors:
            ex.extend(x.exclusion())
        return ex

    def get_order(self) -> Union[int, float]:
        return max([x.get_order() for x in self.factors])

    def get_sub_order(self) -> Union[int, float]:
        return max([x.get_sub_order() for x in self.factors])

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
        return TermNode(self.factors + (other,))

    def __sub__(self, other):
        if isinstance(other, TermNode):
            return self + (-other)
        return TermNode(self.factors + (-other,))

    def __mul__(self, other):
        return (FactorNode() * self) * other

    def __truediv__(self, other):
        return (FactorNode() * self) / other


class FactorNode(StructuralNode):

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
        if len(self.denominator) == 0:
            # only numerator & coefficient
            if len(self.numerator) == 0:
                return NumNode(self.get_coef())
            if len(self.numerator) == 1 and self.get_coef() == 1:
                return self.numerator[0]
        return self

    def is_negative(self) -> bool:
        a, b = self.coef
        return a / b < 0

    def get_add_dim(self):
        # need to remove numbers
        return FactorNode(self.numerator, self.denominator)

    def get_mul_dim(self):
        return FactorNode()

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
                    or c_deno != '1' and len(self.denominator) > 0:
                deno = '({})'.format(deno)
            s += '{}/{}'.format(nu, deno)
        return s

    def __neg__(self):
        # return FactorNode(self.denominator, self.numerator, self.coef[::-1])
        return FactorNode(self.numerator, self.denominator,
                          (-self.coef[0], self.coef[1]))

    def __add__(self, other):
        return (TermNode() + self) + other

    def __sub__(self, other):
        return (TermNode() + self) - other

    def __mul__(self, other):
        if isinstance(other, FactorNode):
            (n, d), (_n, _d) = self.coef, other.coef
            return FactorNode(self.numerator + other.numerator,
                              self.denominator + other.denominator,
                              (n * _n, d * _d))
        return FactorNode(self.numerator + (other,), self.denominator, self.coef)

    def __truediv__(self, other):
        if isinstance(other, FactorNode):
            (n, d), (_n, _d) = self.coef, other.coef
            return FactorNode(self.numerator + other.denominator,
                              self.denominator + other.numerator,
                              (n * _d, d * _n))
        return FactorNode(self.numerator, self.denominator + (other,), self.coef)


# Content Nodes

class ContentNode(MathNode, metaclass=abc.ABCMeta):

    def __neg__(self):
        return mathlib.FactorNode([self], coef=(-1, 1))

    def __add__(self, other):
        return (mathlib.TermNode() + self) + other

    def __sub__(self, other):
        return (mathlib.TermNode() + self) - other

    def __mul__(self, other):
        return (mathlib.FactorNode() * self) * other

    def __truediv__(self, other):
        return (mathlib.FactorNode() * self) / other


# Elementary Nodes

class ElementaryNode(ContentNode, metaclass=abc.ABCMeta):

    def __init__(self, body: MathNode):
        self.body = body

    def is_negative(self) -> bool:
        return False


class ExpoNode(ElementaryNode):

    def __init__(self, body, dim):
        super(ExpoNode, self).__init__(body)
        self.dim = dim

    def simplify(self):
        if isinstance(self.dim, NumNode):
            # Polynomial
            if isinstance(self.body, NumNode):
                return NumNode(self.body.value ** self.dim.value)
            if self.dim.value == 1:
                return self.body
            if self.dim.value < 0:
                return ExpoNode(self.body, -self.dim)

        if isinstance(self.dim, LogNode):
            # e^lnx
            if self.body == self.dim.base:
                return self.dim.body
        return self

    def get_add_dim(self):
        return self

    def get_mul_dim(self):
        return self.body

    def exclusion(self) -> list:
        return [[(self.body, operator.lt, 0), (self.dim, NumNode.is_int, False)]]

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
        return '{}^{}'.format(self.body, self.dim)

    def latex(self) -> str:
        pass


class LogNode(ElementaryNode):

    def __init__(self, base, body):
        super(LogNode, self).__init__(body)
        self.base = base

    def simplify(self):
        if isinstance(self.body, ExpoNode):
            # ln(e^x)
            if self.base == self.body.body:
                return self.body.dim
        return self

    def get_add_dim(self):
        return LogNode(self.base, NumNode(1))

    def get_mul_dim(self):
        return self

    def exclusion(self) -> list:
        return [[(self.base, operator.le, 0),
                 (self.base, operator.eq, 1),
                 (self.body, operator.le, 0)]]

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


class TriNode(ElementaryNode):

    func_dict = {'sin': mathlib.math.sin,
                 'cos': mathlib.math.cos,
                 'tan': mathlib.math.tan}

    @staticmethod
    def mod_pi_2(value):
        return value % (mathlib.math.pi / 2)

    def __init__(self, func, body):
        super(TriNode, self).__init__(body)
        self.func = func

    def simplify(self):
        return self

    def get_add_dim(self):
        return self

    def get_mul_dim(self):
        return self

    def exclusion(self) -> list:
        if self.func == 'tan':
            return [[(self.body, TriNode.mod_pi_2, 0)]]
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

    def get_add_dim(self):
        return self

    def get_mul_dim(self):
        return self.get_add_dim()

    def get_order(self) -> Union[int, float]:
        return 2

    def get_sub_order(self) -> Union[int, float]:
        return ord(self.value)


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

    def is_negative(self) -> bool:
        return self.is_number(self.value) and self.value < 0

    def get_add_dim(self):
        return self if self.is_constant(self.value) else NumNode(1)

    def get_mul_dim(self):
        return self.get_add_dim()

    def get_order(self) -> Union[int, float]:
        return 6

    def get_sub_order(self) -> Union[int, float]:
        return abs(self.value)

    def latex(self) -> str:
        if self.value == 'pi':
            return '\\pi'
        return str(self.value)

    def __neg__(self):
        return NumNode(-1) * self


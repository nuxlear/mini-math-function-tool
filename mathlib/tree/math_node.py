import mathlib
from mathlib import abc, Union
# import mathlib.tree.builder.TermNodeBuilder as TermNodeBuilder
# import mathlib.tree.builder.FactorNodeBuilder as FactorNodeBuilder


class MathNode(metaclass=abc.ABCMeta):
    """ Make immutable """

    # canonicalization

    @abc.abstractmethod
    def is_simplifiable(self) -> bool:
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

    # @abc.abstractmethod
    def exclusion(self):
        pass

    # comparator

    # @abc.abstractmethod
    def __lt__(self, other):
        pass

    # @abc.abstractmethod
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # print

    @abc.abstractmethod
    def __repr__(self):
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


class StructuralNode(MathNode, metaclass=abc.ABCMeta):

    def latex(self) -> str:
        return str(self)


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


class ElementaryNode(ContentNode, metaclass=abc.ABCMeta):

    def __init__(self, body: MathNode):
        self.body = body


class AtomicNode(ContentNode, metaclass=abc.ABCMeta):

    def __init__(self, value):
        self.value = value

    def is_simplifiable(self) -> bool:
        return False

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__[:-4], self.value)

    def __str__(self):
        return '{}'.format(self.value)

    def latex(self) -> str:
        return str(self)


class TermNode(StructuralNode):

    def __init__(self, factors: Union[tuple, list] = tuple()):
        self.factors = tuple(factors)

    def get_add_dim(self):
        return TermNode()

    def get_mul_dim(self):
        return self

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
        self.numerator = tuple(numerator)
        self.denominator = tuple(denominator)
        self.coef = tuple(coef)

    def get_add_dim(self):
        return self     # need to remove numbers

    def get_mul_dim(self):
        return FactorNode()

    def __neg__(self):
        return FactorNode(self.denominator, self.numerator, self.coef[::-1])

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


class VarNode(AtomicNode):

    def get_add_dim(self):
        return self

    def get_mul_dim(self):
        return self.get_add_dim()


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

    def get_add_dim(self):
        return self if self.is_constant(self.value) else NumNode(1)

    def get_mul_dim(self):
        return self.get_add_dim()

    def latex(self) -> str:
        if self.value == 'pi':
            return '\\pi'
        return str(self.value)

    def __neg__(self):
        return NumNode(-self.value)


# class MathNodeFactory:
#
#     @staticmethod
#     def neg(node):
#         pass
# #         if isinstance(node, mathlib.TermNode):



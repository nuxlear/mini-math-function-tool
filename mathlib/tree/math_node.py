import mathlib
from mathlib import abc
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

    @abc.abstractmethod
    def derivative(self):
        pass

    @abc.abstractmethod
    def exclusion(self):
        pass

    # comparator

    @abc.abstractmethod
    def __lt__(self, other):
        pass

    @abc.abstractmethod
    def __eq__(self, other):
        pass

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
        f = mathlib.FactorNodeBuilder()
        f *= self
        return (-f).build()

    def __add__(self, other):
        t = mathlib.TermNodeBuilder()
        t += other
        return t.build()

    def __sub__(self, other):
        t = mathlib.TermNodeBuilder()
        t += -other
        return t.build()

    def __mul__(self, other):
        f = mathlib.FactorNodeBuilder()
        f *= other
        return f.build()

    def __truediv__(self, other):
        f = mathlib.FactorNodeBuilder()
        f /= other
        return f.build()


class StructuralNode(MathNode, metaclass=abc.ABCMeta):

    def latex(self) -> str:
        return str(self)


class ElementaryNode(MathNode, metaclass=abc.ABCMeta):

    def __init__(self, body: MathNode):
        self.body = body


class AtomicNode(MathNode, metaclass=abc.ABCMeta):

    def __init__(self, value):
        self.value = value

    def is_simplifiable(self) -> bool:
        return False

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)

    def __str__(self):
        return '{}'.format(self.value)

    def latex(self) -> str:
        return str(self)


class MathNodeBuilder(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def build(self) -> MathNode:
        pass

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


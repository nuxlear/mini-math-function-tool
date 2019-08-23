import mathlib
from mathlib import Union
# import mathlib.tree.math_node.StructuralNode as StructuralNode


# class TermNode(mathlib.StructuralNode):
#
#     def __init__(self, factors: Union[tuple, list] = tuple()):
#         self.factors = tuple(factors)
#
#     def get_add_dim(self):
#         return TermNode()
#
#     def get_mul_dim(self):
#         return self
#
#     def __neg__(self):
#         factors = [-x for x in self.factors]
#         return TermNode(factors)
#
#     def __add__(self, other):
#         if isinstance(other, TermNode):
#             return TermNode(self.factors + other.factors)
#         return TermNode(self.factors + (other,))
#
#     def __sub__(self, other):
#         if isinstance(other, TermNode):
#             return self + (-other)
#         return TermNode(self.factors + (-other,))
#
#     def __mul__(self, other):
#         return (FactorNode() * self) * other
#
#     def __truediv__(self, other):
#         return (FactorNode() * self) / other
#
#
# class FactorNode(mathlib.StructuralNode):
#
#     def __init__(self, numerator: Union[tuple, list] = tuple(),
#                  denominator: Union[tuple, list] = tuple(),
#                  coef: tuple = (1, 1)):
#         self.numerator = tuple(numerator)
#         self.denominator = tuple(denominator)
#         self.coef = tuple(coef)
#
#     def get_add_dim(self):
#         return self     # need to remove numbers
#
#     def get_mul_dim(self):
#         return FactorNode()
#
#     def __neg__(self):
#         return FactorNode(self.denominator, self.numerator, self.coef[::-1])
#
#     def __add__(self, other):
#         return (TermNode() + self) + other
#
#     def __sub__(self, other):
#         return (TermNode() + self) - other
#
#     def __mul__(self, other):
#         if isinstance(other, FactorNode):
#             (n, d), (_n, _d) = self.coef, other.coef
#             return FactorNode(self.numerator + other.numerator,
#                               self.denominator + other.denominator,
#                               (n * _n, d * _d))
#         return FactorNode(self.numerator + (other,), self.denominator, self.coef)
#
#     def __truediv__(self, other):
#         if isinstance(other, FactorNode):
#             (n, d), (_n, _d) = self.coef, other.coef
#             return FactorNode(self.numerator + other.denominator,
#                               self.denominator + other.numerator,
#                               (n * _d, d * _n))
#         return FactorNode(self.numerator, self.denominator + (other,), self.coef)
#

import mathlib


# class TermNodeBuilder(mathlib.MathNodeFactory):
#
#     def __init__(self):
#         self.factors = []
#
#     def build(self) -> mathlib.TermNode:
#         return mathlib.TermNode(tuple(self.factors))
#
#     def __neg__(self):
#         self.factors = [-x for x in self.factors]
#
#     def __add__(self, other):
#         if isinstance(other, mathlib.TermNode):
#             self.factors.extend(other.factors)
#         else:
#             self.factors.append(other)
#
#     # def __mul__(self, other):
#     #     fb = FactorNodeBuilder()
#
#
# class FactorNodeBuilder(mathlib.MathNodeFactory):
#
#     def __init__(self):
#         self.numerator = []
#         self.denominator = []
#         self.coef = (1, 1)
#
#     def build(self) -> mathlib.FactorNode:
#         self.numerator.sort()
#         self.denominator.sort()
#         self._neaten_coef()
#         return mathlib.FactorNode(tuple(self.numerator), tuple(self.denominator), self.coef)
#
#     def _neaten_coef(self):
#         """ Make coefficient neat. """
#         n, d = self.coef
#         pass
#
#     def update_coef(self, coef):
#         (n, d), (_n, _d) = self.coef, coef
#         coef = n * _n, d * _d
#         self.coef = coef
#
#     def __neg__(self):
#         self.update_coef((-1, 1))
#
#     def __mul__(self, other):
#         if isinstance(other, mathlib.FactorNode):
#             self.numerator += other.numerator
#             self.denominator += other.denominator
#             self.update_coef(other.coef)
#         else:
#             self.numerator.append(other)
#
#     def __truediv__(self, other):
#         if isinstance(other, mathlib.FactorNode):
#             self.numerator += other.denominator
#             self.denominator += other.numerator
#             self.update_coef(other.coef[::-1])
#         else:
#             self.denominator.append(other)
#
#

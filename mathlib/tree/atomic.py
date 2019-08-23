from mathlib.tree.math_node import *


# class VarNode(AtomicNode):
#
#     def get_add_dim(self):
#         return self
#
#     def get_mul_dim(self):
#         return self.get_add_dim()
#
#
# class NumNode(AtomicNode):
#
#     @staticmethod
#     def is_int(value):
#         return isinstance(value, int) or \
#                isinstance(value, float) and value % 1 == 0
#
#     @staticmethod
#     def is_number(value) -> bool:
#         return value.__class__ in [float, int]
#
#     @staticmethod
#     def is_constant(value) -> bool:
#         return value in ['e', 'pi']
#
#     @staticmethod
#     def is_valid_num(value) -> bool:
#         return NumNode.is_number(value) or NumNode.is_constant(value)
#
#     def __init__(self, value):
#         if not NumNode.is_valid_num(value):
#             raise ValueError('invalid number for NumNode: {}'.format(value))
#         if NumNode.is_int(value):
#             value = int(value)
#         super(NumNode, self).__init__(value)
#
#     # def similar_add(self, other) -> bool:
#     #     return isinstance(other, NumNode) and \
#     #            self.is_number(self.value) and self.is_number(other.value)
#     #
#     # def similar_mul(self, other) -> bool:
#     #     return self.similar_add(other)
#
#     def get_add_dim(self):
#         return self if self.is_constant(self.value) else NumNode(1)
#
#     def get_mul_dim(self):
#         return self.get_add_dim()
#
#     def latex(self) -> str:
#         if self.value == 'pi':
#             return '\\pi'
#         return str(self.value)
#
#     def __neg__(self):
#         return NumNode(-self.value)



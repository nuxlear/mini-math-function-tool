from mathlib.core.calculator import *





# inv_op_dict = {
#     '==': '!=', '!=': '==',
#     '<': '>=', '<=': '>', '>': '<=', '>=': '<',
#     'not': 'is', 'is': 'not',
# }
#
#
# def get_domain(exclusion: list):
#     for ex in exclusion:
#
#         for e in ex:
#             # get_solution_from_exclusion(e)
#             if len(e) == 3:
#                 a, cmp, b = e


# def get_solution_from_exclusion(equation):
#     assert len(equation) > 2
#     a, op = equation[:2]
#     while a.__class__ in [TermNode, VarNode]:
#         if isinstance(a, PolyNode):
#             a = a.body
#         if isinstance(a, ExpoNode):
#             a = a.
#
#     if op == '<':
#         pass

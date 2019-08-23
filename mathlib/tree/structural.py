import mathlib
# import mathlib.tree.math_node.StructuralNode as StructuralNode


class TermNode(mathlib.StructuralNode):

    def __init__(self, factors=tuple()):
        self.factors = factors

    def get_add_dim(self):
        return TermNode()

    def get_mul_dim(self):
        return self


class FactorNode(mathlib.StructuralNode):

    def __init__(self, numerator=tuple(), denominator=tuple(), coef=(1, 1)):
        self.numerator = numerator
        self.denominator = denominator
        self.coef = coef

    def get_add_dim(self):
        return self     # need to remove numbers

    def get_mul_dim(self):
        return FactorNode()





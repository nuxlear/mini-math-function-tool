import mathlib
from mathlib.tree.math_node import *


class Calculator:

    def canonicalize(self, node: MathNode):
        exclusion = node.exclusion()

        node = node.simplify()
        exclusion.extend(node.exclusion())

        node = node.merge_similar()
        exclusion.extend(node.exclusion())

        node = node.simplify()
        exclusion.extend(node.exclusion())

        exclusion = self.neaten_exclusion(exclusion)
        return node, exclusion

    def neaten_exclusion(self, exclusion: list):

        def _remove_identical(cond):
            removed = []
            for c in cond:
                n, func, v = c
                if isinstance(n, NumNode):
                    if func(n.eval(), v):
                        # always undefined
                        return None
                    # else:
                    #     continue
                else:
                    removed.append(c)
            return removed

        ex = []
        for x in exclusion:
            x = _remove_identical(x)
            if len(x) > 0 and x not in ex:
                ex.append(x)
        return ex

    def eval(self, node, **kwargs):
        pass




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
            removed = None
            for c in cond:
                n, func, v = c
                n = n.simplify().merge_similar().simplify()
                if isinstance(n, ExpoNode) and func == operator.eq and v in [0, 1]:
                    n = n.body

                if isinstance(n, NumNode):
                    if not func(n.eval(), v):
                        return []   # always in-domain
                else:
                    c = n.simplify(), func, v
                    if removed is None:
                        removed = []
                    removed.append(c)
            return removed

        ex = []
        for x in exclusion:
            x = _remove_identical(x)
            if x is None:
                return x
            if len(x) > 0 and x not in ex:
                ex.append(x)
        return ex

    def eval(self, node, **kwargs):
        node, exclusion = self.canonicalize(node)

        for exs in exclusion:
            cond = False
            for e in exs:
                n, func, v = e
                cond |= func(n.eval(**kwargs), v)
            if cond:
                return mathlib.math.nan

        return node.eval(**kwargs)



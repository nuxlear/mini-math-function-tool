from mathlib.core.node import *
from mathlib.core.node_util import *
from mathlib.core.calculator import is_identity


class NodeSimplifier:

    def __init__(self):
        self.exclusion = []

    def canonicalize(self, node: MathNode):
        _node = node
        # while True:
        #     node = _node
        #     _node = self._preprocess(self.pack(_node))
        #     _node = self._expand(_node)
        #     _node = self._merge_similar(self.pack(self.unpack(_node)))
        #     _node = self._remove_zeros(_node)
        #     self._sort(_node)
        #     if _node == node:
        #         break
        # node = _node
        _node = self.unpack(_node)
        _node = self._preprocess(self.pack(_node))
        _node = self._expand(_node)
        _node = self.unpack(_node)
        _node = self._merge_similar(self.pack(_node))
        _node = self._remove_zeros(_node)
        _node = self.unpack(_node)
        self._neaten_exclusion(_node)
        self._sort(_node)
        node = _node
        return node, self.exclusion

    def pack(self, node):
        if not isinstance(node, TermNode):
            if not isinstance(node, FactorNode):
                node = FactorNode([node], [])
            node = TermNode([node])
        return node

    def unpack(self, node):
        if isinstance(node, TermNode):
            node.factors = [self.unpack(x) for x in node.factors]
            if len(node.factors) == 1:
                # if isinstance(node.factors[0], VarNode):
                #     return PolyNode(node.factors[0], 1)
                return node.factors[0]

        if isinstance(node, FactorNode):
            nu = [self.unpack(x) for x in node.numerator]
            deno = [self.unpack(x) for x in node.denominator]
            if len(nu) == 1 and deno == [] and node.coef == (1, 1):
                return nu[0]
            if nu == [] and deno == [] and node.coef != (1, 1):
                return NumNode(node.coef[0] / node.coef[1])

            nu_factors, deno_factors = [], []
            for x in nu:
                if isinstance(x, TermNode) and len(x.factors) == 1 \
                        and isinstance(x.factors[0], FactorNode) \
                        or isinstance(x, FactorNode):
                    nu_factors.append(x)
            for x in deno:
                if isinstance(x, TermNode) and len(x.factors) == 1 \
                        and isinstance(x.factors[0], FactorNode) \
                        or isinstance(x, FactorNode):
                    deno_factors.append(x)

            nu = [x for x in nu if x not in nu_factors]
            deno = [x for x in deno if x not in deno_factors]
            n = FactorNode(nu, deno, node.coef)

            for x in nu_factors:
                n *= x.factors[0] if isinstance(x, TermNode) else x
            for x in deno_factors:
                n *= x.factors[0].inverse() if isinstance(x, TermNode) else x.inverse()

            if n.numerator == [] and n.denominator == []:
                return NumNode(n.coef[0] / n.coef[1])
            return n

        if isinstance(node, PolyNode):
            if node.dim == 1:
                return self.unpack(node.body)
            return PolyNode(self.unpack(node.body), node.dim)
        if isinstance(node, ExpoNode):
            return ExpoNode(self.unpack(node.base), self.unpack(node.body))
        if isinstance(node, LogNode):
            return LogNode(self.unpack(node.base), self.unpack(node.body))
        if isinstance(node, TriNode):
            return TriNode(node.func, self.unpack(node.body))
        return node

    def _preprocess(self, node: MathNode):
        if isinstance(node, TermNode):
            node.factors = [self._preprocess(x if isinstance(x, FactorNode)
                                             else FactorNode([x])) for x in node.factors]
            if len(node.factors) == 1:
                k = node.factors[0]
                if k.denominator == []:
                    if k.numerator == [] and k.coef != (1, 1):
                        return NumNode(k.coef[0] / k.coef[1])
                    if len(k.numerator) == 1 and k.coef == (1, 1):
                        return k.numerator[0]
            return node

        if isinstance(node, FactorNode):
            node = self._relocate_fraction(node)
            node = self._abbreviate(node)
            return node

        if node.__class__ in [PolyNode, ExpoNode]:
            base, dim = None, None
            if isinstance(node, PolyNode):
                base = self._preprocess(node.body)
                dim = self._preprocess(node.dim)
                if dim % 1 != 0:
                    self.exclusion.append([[base, '<', 0]])
            if isinstance(node, ExpoNode):
                base = self._preprocess(node.base)
                dim = self._preprocess(node.body)
                if isinstance(dim, LogNode):
                    dim_base = self._preprocess(dim.base)
                    dim_body = self._preprocess(dim.body)
                    self.exclusion.append([[dim_base, '<=', 0]])
                    self.exclusion.append([[dim_base, '==', 1]])
                    self.exclusion.append([[dim_body, '<=', 0]])
                    if base.similar_add(dim_base):
                        self.exclusion.append([[base, '<', 0], [dim, 'not', int]])
                        return dim_body

            if isinstance(dim, NumNode):
                if isinstance(base, NumNode):
                    return NumNode(base.value ** dim.value)
                return PolyNode(base, dim.value)
            return node

        if isinstance(node, LogNode):
            base = self._preprocess(node.base)
            body = self._preprocess(node.body)
            self.exclusion.append([[base, '<=', 0]])
            self.exclusion.append([[base, '==', 1]])
            self.exclusion.append([[body, '<=', 0]])
            if isinstance(body, ExpoNode):
                if base.similar_add(body.base):
                    return body.body
                coef = body.body
                body = body.base
                return FactorNode([coef, LogNode(base, body)], [])
            if isinstance(body, PolyNode):
                if base.similar_add(body.body):
                    return NumNode(body.dim)
                coef = body.dim
                body = body.body
                return FactorNode([LogNode(base, body)], [], (coef, 1))
            return node

        if isinstance(node, TriNode):
            # if node.func == 'tan':
            #     self.exclusion.append([[]])
            return node
        return node

    def _relocate_fraction(self, node: FactorNode):
        node.update_coef()
        nu = [self._preprocess(x) for x in node.numerator]
        deno = [self._preprocess(x) for x in node.denominator]

        def invertible(_node):
            if _node.__class__ in [PolyNode, ExpoNode]:
                t = _node.dim if isinstance(_node, PolyNode) else _node.body
                if t.__class__ in [int, float]:
                    return t < 0
                if isinstance(t, NumNode):
                    return t.value < 0
                if isinstance(t, TermNode):
                    return len(t.factors) == 1 \
                           and t.factors[0].coef[0] / t.factors[0].coef[1] < 0
            return False

        def fractional(_node):
            if isinstance(_node, TermNode):
                return len(_node.factors) == 1 and len(_node.factors[0].denominator) > 0
            return False

        nu_invs = [x for x in nu if invertible(x)]
        deno_invs = [x for x in deno if invertible(x)]
        deno_factor = [x for x in deno if fractional(x)]

        nu = [x for x in nu if x not in nu_invs]
        deno = [x for x in deno if x not in deno_invs + deno_factor]
        deno_factor = [x.factors[0] for x in deno_factor]

        new_deno, new_nu = [], []
        for inv in nu_invs:
            if isinstance(inv, PolyNode):
                n = PolyNode(inv.body, negate(inv.dim))
            if isinstance(inv, ExpoNode):
                n = ExpoNode(inv.base, negate(inv.body))
            new_deno.append(n)
        for inv in deno_invs:
            if isinstance(inv, PolyNode):
                n = PolyNode(inv.body, negate(inv.dim))
            if isinstance(inv, ExpoNode):
                n = ExpoNode(inv.base, negate(inv.body))
            new_nu.append(n)

        nu.extend(new_nu)
        deno.extend(new_deno)

        a, b = node.coef
        for x in deno_factor:
            a *= x.coef[0]
            b *= x.coef[1]
            nu.extend(x.denominator)
            deno.extend(x.numerator)
        node.coef = a, b

        return FactorNode(nu, deno, node.coef)

    def _abbreviate(self, node: FactorNode):
        nu, deno = [], [x for x in node.denominator]
        for x in deno:
            self.exclusion.append([[x, '==', 0]])

        for x in node.numerator:
            q = [x for x in deno]
            for y in q:
                if x.similar_mul(y):
                    deno.remove(y)
                    k, a = compare_dim(x, y)
                    if k is None:
                        n = ExpoNode(x.base, TermNode([
                            FactorNode([x.body]), FactorNode([negate(y.body)])]))
                        nu.append(n)
                    elif k < 0:
                        if isinstance(y, ExpoNode):
                            n = ExpoNode(y.base, TermNode([
                                # FactorNode([y.body]), FactorNode([], [], (-a, 1))]))
                                FactorNode([y.body]), NumNode(-a)]))
                        if isinstance(y, PolyNode):
                            n = PolyNode(y.body, -a)
                        deno.append(n)
                    elif k > 0:
                        if isinstance(x, ExpoNode):
                            n = ExpoNode(x.base, TermNode([
                                # FactorNode([x.body]), FactorNode([], [], (-a, 1))]))
                                FactorNode([x.body]), NumNode(-a)]))
                        if isinstance(x, PolyNode):
                            n = PolyNode(x.body, a)
                        nu.append(n)
                    elif k == 0:
                        pass
                    break
            else:
                nu.append(x)

        return FactorNode(nu, deno, node.coef)

    def _expand(self, node):
        return node

    def _merge_similar(self, node: MathNode):
        self._sort(node)
        if isinstance(node, TermNode):
            factors = self._merge_add([self._merge_similar(x if isinstance(x, FactorNode) else FactorNode([x])) for x in node.factors])
            return TermNode(factors)
        if isinstance(node, FactorNode):
            nu = self._merge_mul([self._merge_similar(x) for x in node.numerator])
            deno = self._merge_mul([self._merge_similar(x) for x in node.denominator])
            return FactorNode(nu, deno, node.coef)
        if isinstance(node, PolyNode):
            body = self._merge_similar(node.body)
            return PolyNode(body, node.dim)
        if isinstance(node, TriNode):
            body = self._merge_similar(node.body)
            return TriNode(node.func, body)
        if isinstance(node, ExpoNode):
            base = self._merge_similar(node.base)
            body = self._merge_similar(node.body)
            # self.exclusion.append([[base, '<', 0], [body, 'not', int]])
            return ExpoNode(base, body)
        if isinstance(node, LogNode):
            base = self._merge_similar(node.base)
            body = self._merge_similar(node.body)
            return LogNode(base, body)
        return node

    def _merge_add(self, node_list: list) -> list:
        node_list = [x for x in node_list if x is not None]
        sim_list = []
        for x in node_list:
            for s in sim_list:
                if s.similar_add(x):
                    s += x
                    break
            else:
                sim_list.append(x)
        return sim_list

    def _merge_mul(self, node_list: list) -> list:
        node_list = [x for x in node_list if x is not None]
        sim_list = []
        for x in node_list:
            q = []
            for s in sim_list:
                if s.similar_mul(x):
                    q.append(s * x)
                    break
                else:
                    q.append(s)
            else:
                q.append(x)
            sim_list = q
        return sim_list

    def _remove_zeros(self, node: MathNode):
        if isinstance(node, TermNode):
            node.factors = [x for x in node.factors if not self._is_zero(x)]
        return node

    def _is_zero(self, node: MathNode):
        if isinstance(node, TermNode):
            return len(node.factors) == 0
        if isinstance(node, FactorNode):
            if node.coef[0] == 0:
                return True
            for x in node.numerator:
                if self._is_zero(x):
                    return True
            return False
        if isinstance(node, NumNode):
            return node.value == 0
        if isinstance(node, PolyNode):
            return self._is_zero(node.body)
        if isinstance(node, ExpoNode):
            return self._is_zero(node.base)
        return False
        # if isinstance(node, LogNode):
        #     return self._is_one(node.body)
        # if isinstance(node, TriNode):
        #     return node.func in ['sin', 'tan'] and self._is_zero(node.body) \
        #         or node.func == 'cos' and self._is_one(node.body)

    def _neaten_exclusion(self, node: MathNode):
        self._exclude(node)

        exclusion = []
        for e in self.exclusion:
            if e in exclusion:
                continue
            equations = []
            for _e in e:
                if not is_identity(_e):
                    equations.append(_e)
            if len(equations) > 0:
                exclusion.append(equations)

        for e in exclusion:
            for _e in e:
                if isinstance(_e[0], PolyNode) and _e[0].dim == 1:
                    _e[0] = _e[0].body

        self.exclusion = exclusion

    def _exclude(self, node: MathNode):
        if isinstance(node, TermNode):
            for x in node.factors:
                self._exclude(x)
        if isinstance(node, FactorNode):
            for x in node.numerator + node.denominator:
                self._exclude(x)
        if isinstance(node, PolyNode):
            if node.dim % 1 != 0:
                self.exclusion.append([[node.body, '<', 0]])
        if isinstance(node, ExpoNode):
            self.exclusion.append([[node.base, '<', 0], [node.body, 'not', int]])
        if isinstance(node, LogNode):
            self.exclusion.append([[node.base, '<=', 0]])
            self.exclusion.append([[node.base, '==', 1]])
            self.exclusion.append([[node.body, '<=', 0]])
        if isinstance(node, TriNode):
            if node.func == 'tan':
                self.exclusion.append([[node.body, '%', math.pi, '==', 0.5*math.pi]])

    def _sort(self, node: MathNode):
        if isinstance(node, TermNode):
            for x in node.factors:
                self._sort(x)
            node.factors.sort()
        if isinstance(node, FactorNode):
            for x in node.numerator + node.denominator:
                self._sort(x)
            node.numerator.sort()
            node.denominator.sort()
        if isinstance(node, PolyNode):
            self._sort(node.body)
        if isinstance(node, ExpoNode) or isinstance(node, LogNode):
            self._sort(node.base)
            self._sort(node.body)
        if isinstance(node, TriNode):
            self._sort(node.body)


if __name__ == '__main__':
    pass

from mathlib.core.node import *
from mathlib.utils.node_util import *


class LaTeXGenerator:

    def generate(self, node: MathNode):
        s = self._generate(node)
        if s == '':
            return '0'
        return s

    def _generate(self, node: MathNode):
        if node.__class__ in [int, float]:
            return str(node)

        if isinstance(node, TermNode):
            if len(node.factors) == 0:
                return ''
            s = self._generate(node.factors[0])
            for x in node.factors[1:]:
                if is_negative(x):
                    s += ' - {}'.format(self._generate(-x))
                else:
                    s += ' + {}'.format(self._generate(x))
            return '{}'.format(s)

        if isinstance(node, FactorNode):
            s = ''
            if node.coef[0] / node.coef[1] < 0:
                s += '-'
            c_nu = '{}'.format(abs(node.coef[0]))
            c_deno = '{}'.format(abs(node.coef[1]))

            def _pack_term(node):
                if isinstance(node, TermNode):
                    return '({})'.format(self.generate(node))
                return self._generate(node)

            nu = '{}'.format(''.join(map(_pack_term, node.numerator)))
            deno = '{}'.format(''.join(map(_pack_term, node.denominator)))

            if deno == '':
                if c_deno != '1':
                    s += '{{{{{}}} \\over {{{}}}}}'.format(c_nu, c_deno)
                else:
                    if c_nu != '1' or nu == '':
                        s += '{{{}}}'.format(c_nu)

                if nu != '':
                    s += '{{{}}}'.format(nu)
            else:
                if c_nu != '1' or nu == '':
                    nu = '{{{}}}{}'.format(c_nu, nu)
                if c_deno != '1':
                    deno = '{{{}}}{}'.format(c_deno, deno)
                s += '{{{} \\over {}}}'.format(nu, deno)
            return s

        if isinstance(node, PolyNode):
            body = '{{{}}}'.format(self._generate(node.body))
            if node.body.__class__ not in [VarNode, NumNode]:
                body = '({})'.format(body)
            return '{{{}}}^{{{}}}'.format(body, node.dim)

        if isinstance(node, ExpoNode):
            base = '{{{}}}'.format(self._generate(node.base))
            body = '{{{}}}'.format(self._generate(node.body))
            if node.base.__class__ not in [VarNode, NumNode]:
                base = '({})'.format(base)
            if node.body.__class__ not in [VarNode, NumNode]:
                body = '({})'.format(body)
            return '{{{}}}^{{{}}}'.format(base, body)

        if isinstance(node, LogNode):
            s = '\\'
            if isinstance(node.base, NumNode):
                if node.base.value == math.e:
                    s += 'ln'
                elif node.base.value == 10:
                    s += 'log'
                else:
                    s += 'log_{{{}}}'.format(node.base.value)
            else:
                s += 'log_{{{}}}'.format(self._generate(node.base))
            body = ' {{{}}}'.format(self._generate(node.body))
            if node.body.__class__ not in [VarNode, NumNode]:
                body = '({})'.format(body)
            s += body
            return s

        if isinstance(node, TriNode):
            body = '{{{}}}'.format(self._generate(node.body))
            if node.body.__class__ not in [VarNode, NumNode]:
                body = '({})'.format(body)
            return '\\{} {}'.format(node.func, body)

        if isinstance(node, NumNode):
            return '{{{}}}'.format(node.value)

        if isinstance(node, VarNode):
            return node.name

    def _generate_fraction(self, nodes: list, coef):
        s = ''
        if len(nodes) == 0:
            s += '{}'.format(coef)
        elif coef == -1:
            s += '-'
        elif coef != 1:
            s += '{}'.format(coef)
        s += '{}'.format(''.join(map(self._generate, nodes)))

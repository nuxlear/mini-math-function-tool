from mathlib.core.node import *
from mathlib.utils.node_util import *


class LaTeXGenerator:

    def generate(self, node: MathNode):
        s = self._generate(node)
        if s == '':
            return '0'
        if s[0] == '(' and s[-1] == ')':
            return s[1:-1]
        return s

    def _generate(self, node: MathNode):
        if isinstance(node, TermNode):
            if len(node.factors) == 0:
                return ''
            s = self._generate(node.factors[0])
            for x in node.factors[1:]:
                if is_negative(x):
                    s += ' - {}'.format(self._generate(negate(x)))
                else:
                    s += ' + {}'.format(self._generate(x))
            return '({})'.format(s)

        if isinstance(node, FactorNode):
            s = ''
            if node.coef[0] / node.coef[1] < 0:
                s += '-'
            c_nu = '{}'.format(abs(node.coef[0]))
            c_deno = '{}'.format(abs(node.coef[1]))

            nu = '{}'.format(''.join(map(self._generate, node.numerator)))
            deno = '{}'.format(''.join(map(self._generate, node.denominator)))

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
            return '{{{}}}^{{{}}}'.format(self._generate(node.body), node.dim)

        if isinstance(node, ExpoNode):
            return '{{{}}}^{{{}}}'.format(self._generate(node.base),
                                          self._generate(node.body))

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
            s += ' {{{}}}'.format(self._generate(node.body))
            return s

        if isinstance(node, TriNode):
            return '\\{} {{{}}}'.format(node.func, self._generate(node.body))

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

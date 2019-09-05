from mathlib.tree.math_node import *


class ParseNode:

    def __init__(self, value, type, parent):
        self.value = value
        self.type = type
        self.parent = parent

        self.childs = []

    def add_child(self, node):
        self.childs.append(node)

    def __str__(self):
        if self.is_terminal():
            return '{} -> `{}`'.format(self.type, self.value)
        else:
            return '{} -> [{}]'.format(self.type, ', '.join(map(str, self.childs)))

    def is_terminal(self):
        return self.value is not None


class NodeBuilder:

    def build(self, parse_tree: ParseNode):
        return self._traverse(parse_tree)

    def _traverse(self, node: ParseNode) -> MathNode:
        if node.type in ['expr', 'term', 'body']:
            return self._flatten(node)

        if node.type == 'factor':
            prefix, body = node.childs
            n = self._traverse(body)
            if len(prefix.childs) > 0:
                n = -n
            return n#.simplify()

        if node.type in ['expo', 'function', 'funbody']:
            if len(node.childs) > 1:
                return self._traverse(node.childs[1])  # ( expr )
            return self._traverse(node.childs[0])

        if node.type == 'triangular':
            func_name = node.childs[0].childs[0].value
            return TriNode(func_name, self._traverse(node.childs[1]))

        if node.type == 'logarithm':
            return LogNode(self._traverse(node.childs[1]), self._traverse(node.childs[3]))

        if node.type == 'var':
            return VarNode(node.childs[0].value)

        if node.type == 'num':
            val = node.childs[0].value
            if val not in ['e', 'pi']:
                val = float(val)
            return NumNode(val)

    def _flatten(self, node: ParseNode):
        cur = node
        if node.type == 'expr':
            factors = [self._traverse(cur.childs[0])]
            cur = cur.childs[1]

            while len(cur.childs) > 0:
                f = self._traverse(cur.childs[1])
                if cur.childs[0].childs[0].value == '-':
                    f = -f
                factors.append(f)
                cur = cur.childs[2]

            return TermNode(factors)#.simplify()

        if node.type == 'term':
            nu = [self._traverse(cur.childs[0])]
            deno = []
            cur = cur.childs[1]

            while len(cur.childs) > 0:
                op = cur.childs[0].childs[0].value
                n = self._traverse(cur.childs[1])
                if op == '*':
                    nu.append(n)
                if op == '/':
                    deno.append(n)
                cur = cur.childs[2]

            return FactorNode(nu, deno)#.simplify()

        if node.type == 'body':
            base = self._traverse(cur.childs[0])
            cur = cur.childs[1]

            while len(cur.childs) > 0:
                n = self._traverse(cur.childs[1])
                base = ExpoNode(base, n)#.simplify()
                cur = cur.childs[2]

            return base#.simplify()


if __name__ == '__main__':
    pass

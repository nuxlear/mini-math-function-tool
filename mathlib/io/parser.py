import itertools
from collections import OrderedDict

from mathlib.io.lexer import Lexer, TokenStream
from mathlib.core.node import *


class Parser:

    def __init__(self, filename=None, lexer=None):

        self.grammar = OrderedDict()
        self.first = OrderedDict()
        self.follow = OrderedDict()
        self.table = OrderedDict()

        if lexer is not None:
            self.lexer = lexer
        if filename is not None:
            self.read_grammar(filename)

    def read_grammar(self, filename):
        with open(filename, 'r') as f:
            lines = self._read_lines(f.readlines())

            for line in lines:
                # line = self._apply_lex(line)
                left, right = self._read_grammar_line(line)
                self.grammar[left] = right

        self.make_table()

    @staticmethod
    def _read_lines(lines):
        newlines = []
        tokens = None
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            i += 1

            if len(line) == 0 or line[0] == '#':
                continue
            if line[0] == '|':
                tokens.extend(line.split())
            else:
                if tokens is not None:
                    newlines.append(tokens)
                tokens = line.split()
        newlines.append(tokens)

        return newlines

    def _apply_lex(self, line):
        if not hasattr(self, 'lexer') or self.lexer is None:
            raise ValueError('lexer must not be None. ')

        newline = []
        for token in line:
            if token in self.lexer.tokens:
                token = self.lexer.tokens[token]
            newline.append(token)

        return newline

    @staticmethod
    def _read_grammar_line(line):
        if line[1] != '->':
            raise SyntaxError('expect "->" in {}'.format(' '.join(line)))

        left = line[0]
        right = list([list(x) for i, x in
                       itertools.groupby(line[2:], lambda x: x == '|') if not i])

        if len(right) == 0:
            raise SyntaxError('no grammar is given: {}'.format(left))

        return left, right

    def make_table(self):
        for token in self.lexer.get_tokens():
            self.get_first(token)

        for key in self.grammar.keys():
            self.get_first(key)
            for gram in self.grammar[key]:
                self.get_first(gram)

        for key in self.grammar.keys():
            self.get_follow(key)

        for key in self.grammar.keys():
            for gram in self.grammar[key]:
                ll = self.get_lookahead(key, gram)
                for t in ll:
                    self.table[(key, t)] = gram

    def get_first(self, key):
        if isinstance(key, list):
            if len(key) == 1:
                return self.get_first(key[0])

            first = self.get_first(key[0])
            if '@' not in first:
                return first
            return first.union(self.get_first(key[1:]))

        assert isinstance(key, str)

        if key in self.first:
            return self.first[key]

        if self.is_terminal(key):
            # return {self.lexer.tokens[key]}
            first = {key}
        elif key == '@':
            first = {'@'}
        else:
            first = set()
            for gram in self.grammar[key]:
                first.update(self.get_first(gram))

        self.first[key] = first
        return first

    def get_follow(self, key):
        if self.is_terminal(key):
            follow = self.follow[key] = {key}
            return follow

        follow = set()
        if key == 'expr':
            follow.add('$')

        for k in self.grammar.keys():
            for gram in self.grammar[k]:
                if key not in gram:
                    continue

                i = gram.index(key)
                if i == len(gram) - 1:
                    if key != k:
                        follow = self.get_follow(k)

                j = i + 1
                while j < len(gram):
                    next = gram[j]

                    follow.update(self.get_first(next))
                    if self.is_nullable(next):
                        follow.discard('@')
                    else:
                        break
                    j += 1

                if j == len(gram):
                    if key != k:
                        follow.update(self.get_follow(k))

        self.follow[key] = follow
        return follow

    def get_lookahead(self, left, right):
        return self.ringsum(self.get_first(right), self.get_follow(left))

    @staticmethod
    def is_terminal(key: str):
        return key[0].isupper()

    def is_nullable(self, key: str):
        assert key in self.first, 'the nullable check must be called after first set is calculated.'
        return '@' in self.first[key]

    @staticmethod
    def ringsum(a: set, b: set):
        if '@' in a:
            u = a.union(b)
            u.discard('@')
            return u
        return a

    def parse(self, stream: TokenStream):
        stack = [('$', None), ('expr', None)]
        root = None
        cur = None

        while True:
            if not stream.is_end():
                token, terminal = stream.current()

                if self.is_terminal(stack[-1][0]):
                    if stack[-1][0] == terminal:
                        print('consuming {}'.format(token))

                        t, parent = stack.pop()
                        n = ParseNode(token, t, parent)
                        parent.add_child(n)
                        stream.next()
                    else:
                        raise ValueError('token and grammar rule doesn\'t match: {} with {}'.format(terminal, gram))

                else:
                    key = (stack[-1][0], terminal)

                    if key in self.table:
                        gram = self.table[key]
                    else:
                        raise ValueError('Parse Error: expected `{}` in next token.'.format(', '.join(self.first[stack[-1]])))

                    t, parent = stack.pop()
                    n = ParseNode(None, t, parent)
                    if parent is None:
                        root = n
                    else:
                        parent.add_child(n)
                    cur = n

                    if gram != ['@']:
                        stack.extend([(t, cur) for t in gram[::-1]])
                        # stack.extend(gram[::-1])
            else:
                if stack[-1][0] == '$':
                    break
                if self.is_nullable(stack[-1][0]):
                    t, parent = stack.pop()
                    n = ParseNode(None, t, parent)
                    parent.add_child(n)
                else:
                    raise ValueError('Parse Error: un-consumed token: {}'.format(stack[-1]))

        return root


if __name__ == '__main__':
    l = Lexer('lexer_grammar')
    s = Parser('parser_grammar', l)
    print('\n\t===== FIRST =====')
    for k, v in s.first.items():
        print('{} = {}'.format(k, v))
    print('\n\t===== FOLLOW =====')
    for k, v in s.follow.items():
        print('{} = {}'.format(k, v))
    print('\n\t===== TABLE =====')
    for k, v in s.table.items():
        print('{} = {}'.format(k, v))

    # tree = s.parse(l.stream('3*sinx^2'))
    # tree = s.parse(l.stream('3*sinx + 4*cosx * 5^2'))
    # tree = s.parse(l.stream('x^3-2*x^2+4/7*x-10'))
    # tree = s.parse(l.stream('-1 * 3 - -5'))
    # tree = s.parse(l.stream('-5*log2_x^3+x^8-3.5^x'))
    # tree = s.parse(l.stream('logx_y/x'))
    # tree = s.parse(l.stream('1 + x^3 - 4*x - x^2'))
    tree = s.parse(l.stream('sinx*x*-4*log2_(x^2)'))
    # tree = s.parse(l.stream('(x-1)^2 + 13*(x-1) - 7'))
    print(tree)

    b = NodeBuilder().build(tree)
    print(b)
    print(b.eval(x=3, y=7))

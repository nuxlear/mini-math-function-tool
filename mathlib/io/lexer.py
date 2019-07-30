import itertools
from collections import OrderedDict
from typing import Union
import re


class TokenStream:

    def __init__(self, tokens, terminals):
        assert len(tokens) == len(terminals)

        self.tokens = tokens
        self.terminals = terminals

        self.len = len(tokens)
        self.i = 0

    def __len__(self):
        return self.len

    def current(self):
        return self.tokens[self.i], self.terminals[self.i]

    def cur_token(self):
        return self.tokens[self.i]

    def cur_terminal(self):
        return self.terminals[self.i]

    def next(self):
        self.i += 1

    def has_next(self):
        return self.i < len(self) - 1

    def is_end(self):
        return self.i >= len(self)


class Lexer:

    def __init__(self, filename=None):

        self.tokens = OrderedDict()
        self.terminals = OrderedDict()

        if filename is not None:
            self.read_grammar(filename)
            self.terminals = dict([(v, k) for k, v in self.tokens.items()])

    def read_grammar(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()

            for line in lines:
                line = line.strip()
                if len(line) == 0 or line[0] == '#':
                    continue
                item = line.split()
                if len(item) != 2:
                    raise SyntaxError(
                        'lexer grammar must be like `name, string`, with length 2: {}'.format(' '.join(item)))
                left, right = item
                self.tokens[left] = right

    def tokenize(self, string: str):

        def get_pattern(tokens):
            chars = [x for x in tokens if len(x) == 1]
            patterns = [x for x in tokens if x not in chars]

            patterns.append('[{}]'.format(''.join(chars)).replace('-', '\\-'))

            return '({})'.format('|'.join(map(lambda x: '({})'.format(x), patterns)))

        def find_terminal(token):
            regexs = {}
            for k, v in self.tokens.items():
                regexs[k] = re.compile(v) if len(v) > 1 else re.compile('\\' + v)

            for k in self.tokens.keys():
                r, v = regexs[k], self.tokens[k]
                x = r.match(token)
                if x is not None:
                    return k
            return None

        pattern = get_pattern(self.tokens.values())
        regex = re.compile(pattern)
        tokens = [x[0] for x in regex.findall(string)]
        terminals = [find_terminal(x) for x in tokens]
        return tokens, terminals

    def get_tokens(self):
        return tuple(self.tokens.keys())

    def stream(self, inputs: Union[tuple, list, str]):
        if len(inputs) == 2:
            assert type(inputs) in [tuple, list]
            s = TokenStream(*inputs)
        else:
            assert isinstance(inputs, str)
            s = TokenStream(*self.tokenize(inputs))

        return s


if __name__ == '__main__':
    l = Lexer('lexer_grammar')
    s = l.tokens
    # print(s)
    t = l.tokenize('3sinx + 4cosx * 5^2')
    print(t)

    s = l.stream(t)
    print(s.current())

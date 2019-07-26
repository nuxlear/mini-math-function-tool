import itertools
from collections import OrderedDict
import re


class Lexer:

    def __init__(self, filename=None):

        self.tokens = OrderedDict()

        if filename is not None:
            self.read_grammar(filename)

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

    def tokenize(self, string):

        def get_pattern(tokens):
            chars = [x for x in tokens if len(x) == 1]
            patterns = [x for x in tokens if x not in chars]

            patterns.append('[{}]'.format(''.join(chars)).replace('-', '\\-'))

            return '({})'.format('|'.join(map(lambda x: '({})'.format(x), patterns)))

        pattern = get_pattern(self.tokens.values())
        regex = re.compile(pattern)
        tokens = [x[0] for x in regex.findall(string)]
        return tokens

    def get_tokens(self):
        return tuple(self.tokens.keys())


if __name__ == '__main__':
    l = Lexer('lexer_grammar')
    s = l.tokens
    # print(s)
    t = l.tokenize('3sinx + 4cosx * 5^2')
    print(t)

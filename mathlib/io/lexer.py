from collections import OrderedDict


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

    @staticmethod
    def tokenize(string):
        pass

    def get_tokens(self):
        return tuple(self.tokens.keys())


if __name__ == '__main__':
    s = Lexer('lexer_grammar').tokens
    print(s)

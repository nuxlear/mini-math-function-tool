

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


from mathlib.core import *
from mathlib.io import *
from mathlib.ui import *


from datetime import datetime
from flask import Flask, render_template, request
math_app = Flask(__name__)


default_lexer_grammar = 'mathlib/io/lexer_grammar'
default_parser_grammar = 'mathlib/io/parser_grammar'

lexer = Lexer(default_lexer_grammar)
parser = Parser(default_parser_grammar, lexer)

builder = NodeBuilder()
simplifier = NodeSimplifier()
calculator = Calculator(simplifier)
plotter = Plotter()
latex = LaTeXGenerator()


@math_app.route('/')
def home():
    timestamp = str(datetime.now().timestamp())
    return render_template('home.html', timestamp=timestamp)


@math_app.route('/post', methods=['POST', 'GET'])
def get_notation():
    if request.method == 'POST':
        inputs = request.form
        notation = inputs['notation']
        var = inputs['variable'] if 'variable' in inputs else 'x'

        tree = parser.parse(lexer.stream(notation))
        tree = builder.build(tree)
        fx, ex = simplifier.canonicalize(tree)
        dfx, dex = calculator.derivate(fx, ex, var)

        result = {'notation': '$$ {} $$'.format(latex.generate(fx)),
                  'exclusions': ex,
                  'derivative': '$$ {} $$'.format(latex.generate(dfx)),
                  'exclusions (derivative)': dex}

        timestamp = str(datetime.now().timestamp())
        return render_template('home.html', result=result, timestamp=timestamp)


if __name__ == '__main__':
    math_app.run(debug=True)


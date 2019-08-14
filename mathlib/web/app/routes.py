from mathlib.core import *
from mathlib.io import *
from mathlib.ui import *


import os
from datetime import datetime
from flask import Flask, render_template, request
math_app = Flask(__name__)
math_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


app_root = os.path.dirname(__file__)
image_dir = os.path.join(app_root, 'static', 'image')

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
    lim = (-10, 10)
    return render_template('home.html', timestamp=timestamp, lim=lim)


@math_app.route('/post', methods=['POST', 'GET'])
def get_notation():
    if request.method == 'POST':
        inputs = request.form
        notation = inputs['notation']
        var = inputs['variable'] if 'variable' in inputs else 'x'
        lim = float(inputs['low']), float(inputs['high'])

        tree = parser.parse(lexer.stream(notation))
        tree = builder.build(tree)
        fx, ex = simplifier.canonicalize(tree)
        dfx, dex = calculator.derivate(fx, ex, var)

        fname = 'fig.png'
        fig, ax = plotter.draw_plot(fx, ex, var, lim, 'f(x)')
        fig, ax = plotter.draw_plot(dfx, dex, var, lim, 'f\'(x)', fig=fig, ax=ax)
        fig.savefig(os.path.join(image_dir, fname))

        result = {'notation': '$$ {} $$'.format(latex.generate(fx)),
                  'exclusions': ex,
                  'derivative': '$$ {} $$'.format(latex.generate(dfx)),
                  'exclusions (derivative)': dex,
                  'Graph': fname}

        timestamp = str(datetime.now().timestamp())
        return render_template('home.html', result=result, timestamp=timestamp, lim=lim)


if __name__ == '__main__':
    math_app.run(debug=True)


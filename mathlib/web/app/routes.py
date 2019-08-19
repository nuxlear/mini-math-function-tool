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


@math_app.errorhandler(500)
def server_error(error):
    error_msg = 'Calculation failed!'
    timestamp = str(datetime.now().timestamp())
    lim = (-10, 10)
    return render_template('home.html', timestamp=timestamp, lim=lim, error_msg=error_msg)


@math_app.route('/')
def home():
    timestamp = str(datetime.now().timestamp())
    lim = (-10, 10)
    return render_template('home.html', timestamp=timestamp, lim=lim)


@math_app.route('/post', methods=['POST', 'GET'])
def get_notation():
    lexer = math_app.config['lexer']
    parser = math_app.config['parser']
    builder = math_app.config['builder']
    simplifier = math_app.config['simplifier']
    calculator = math_app.config['calculator']
    plotter = math_app.config['plotter']
    latex = math_app.config['latex']

    def _get_condition_dict(conditions: str):
        strip = lambda x: x.strip()
        conds = list(map(strip, conditions.split(',')))
        cond_dict = {}
        for c in conds:
            if '=' not in c:
                continue
            a, b = map(strip, c.split('='))
            cond_dict[a] = float(b)
        return cond_dict

    if request.method == 'POST':
        inputs = request.form
        notation = inputs['notation']
        conditions = _get_condition_dict(inputs['conditions'])
        # var = inputs['variable'] if 'variable' in inputs else 'x'
        var = inputs['variable']
        # TODO: check given variables and choose return HTML
        lim = float(inputs['low']), float(inputs['high'])

        tree = parser.parse(lexer.stream(notation))
        tree = builder.build(tree)
        fx, ex = simplifier.canonicalize(tree)
        dfx, dex = calculator.derivate(fx, ex, var)

        fname = 'fig.png'
        fig, ax, values = plotter.draw_plot(fx, ex, var, lim, 'f({})'.format(var), **conditions)
        fig, ax, values = plotter.draw_plot(dfx, dex, var, lim, 'f\'({})'.format(var),
                                            fig=fig, ax=ax, values=values, **conditions)
        fig.savefig(os.path.join(image_dir, fname))

        result = {'notation': '$$ {} $$'.format(latex.generate(fx)),
                  'string': str(fx),
                  'derivative': '$$ {} $$'.format(latex.generate(dfx)),
                  'string (derivative)': str(dfx),
                  'Graph': fname}

        timestamp = str(datetime.now().timestamp())
        return render_template('home.html', result=result, timestamp=timestamp,
                               lim=lim, notation=notation, conditions=inputs['conditions'])


if __name__ == '__main__':
    #
    # default_lexer_grammar = 'mathlib/io/lexer_grammar'
    # default_parser_grammar = 'mathlib/io/parser_grammar'
    #
    # lexer = Lexer(default_lexer_grammar)
    # parser = Parser(default_parser_grammar, lexer)
    #
    # builder = NodeBuilder()
    # simplifier = NodeSimplifier()
    # calculator = Calculator(simplifier)
    # plotter = Plotter()
    # latex = LaTeXGenerator()

    math_app.run(debug=True)


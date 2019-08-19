from mathlib.core import *
from mathlib.io import *
from mathlib.ui import *

from mathlib.core.node import *
from mathlib.utils.node_util import *

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

            t = parser.parse(lexer.stream(b))
            t = builder.build(t)
            f, e = simplifier.canonicalize(t)
            b = calculator.eval(f, e)

            cond_dict[a] = float(b)
        return cond_dict

    def print_exclusion(exclusion):
        cmp_dict = {
            '==': '=', '!=': '\\ne', '<=': '\\leq', '>=': '\\geq',
            'not': '\\notin', 'is': '\\in'
        }
        domain_dict = {int: '\\Z', float: '\\R'}

        _exclusion = []
        for ex in exclusion:
            if ex in _exclusion:
                continue
            _exclusion.append(ex)
        exclusion = _exclusion

        ex_latex = []
        for ex in exclusion:
            tmp = []
            for e in ex:
                a, op, m, cmp, b = [None] * 5
                if len(e) == 3:
                    a, cmp, b = e
                if len(e) == 5:
                    a, op, m, cmp, b = e
                    if op == '%':
                        a = '{{{}}} mod {{{}}}'.format(latex.generate(a),
                                                       latex.generate(m))
                if cmp in cmp_dict:
                    cmp = cmp_dict[cmp]
                if b in domain_dict:
                    b = domain_dict[b]
                tmp.append('{{{}}} {} {}'.format(latex.generate(a), cmp, b))
            ex_latex.append('$$ {} $$'.format(', '.join(tmp)))
        return ex_latex

    if request.method == 'POST':
        inputs = request.form
        notation = inputs['notation']
        conditions = _get_condition_dict(inputs['conditions'])
        lim = float(inputs['low']), float(inputs['high'])

        tree = parser.parse(lexer.stream(notation))
        tree = builder.build(tree)
        fx, ex = simplifier.canonicalize(tree)

        ex_latex = print_exclusion(ex)

        var_not = get_unique_vars(tree)
        var_cond = {k for k in conditions.keys()}
        var_left = var_not.difference(var_cond)

        if len(var_left) > 1:
            error_msg = 'Not enough variables are given'
            result = {}
            timestamp = str(datetime.now().timestamp())
            return render_template('home.html', result=result, timestamp=timestamp,
                                   lim=lim, notation=notation, conditions=inputs['conditions'], error_msg=error_msg)

        if len(var_left) == 1:
            var = list(var_left)[0]
            dfx, dex = calculator.derivate(fx, ex, var)

            dex_latex = print_exclusion(dex)

            fname = 'fig.png'
            fig, ax, values = plotter.draw_plot(fx, ex, var, lim, 'f({})'.format(var), **conditions)
            fig, ax, values = plotter.draw_plot(dfx, dex, var, lim, 'f\'({})'.format(var),
                                                fig=fig, ax=ax, values=values, **conditions)
            os.makedirs(image_dir, exist_ok=True)
            fig.savefig(os.path.join(image_dir, fname))

            result = {'notation': '$$ {} $$'.format(latex.generate(fx)),
                      'string': str(fx),
                      'derivative': '$$ {} $$'.format(latex.generate(dfx)),
                      'string (derivative)': str(dfx),
                      'Graph': fname,
                      'exclusion': ex_latex,
                      'exclusion (derivative)': dex_latex}

            timestamp = str(datetime.now().timestamp())
            return render_template('home.html', result=result, timestamp=timestamp,
                                   lim=lim, notation=notation, conditions=inputs['conditions'])

        if len(var_left) == 0:
            # go to eval mode
            answer = calculator.eval(fx, ex, **conditions)

            result = {'notation': '$$ {} $$'.format(latex.generate(fx)),
                      'string': str(fx),
                      'evaluation': answer,
                      'exclusion': ex_latex}

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


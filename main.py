import mathlib


def main(lexer=None, parser=None, builder=None, simplifier=None, calculator=None,
         plotter=None, latex=None, gui=False):
    lexer = lexer or mathlib.Lexer(mathlib.default_lexer_grammar)
    parser = parser or mathlib.Parser(mathlib.default_parser_grammar, lexer)

    builder = builder or mathlib.NodeBuilder()
    simplifier = simplifier or mathlib.NodeSimplifier()
    calculator = calculator or mathlib.Calculator(simplifier)
    plotter = plotter or mathlib.Plotter()
    latex = latex or mathlib.LaTeXGenerator()

    if gui:
        math_app = mathlib.math_app
        math_app.config['lexer'] = lexer
        math_app.config['parser'] = parser
        math_app.config['builder'] = builder
        math_app.config['simplifier'] = simplifier
        math_app.config['calculator'] = calculator
        math_app.config['plotter'] = plotter
        math_app.config['latex'] = latex

        mathlib.math_app.run()

    else:
        print(mathlib.manual())
        while True:
            s = input('>>> ')
            if s.strip() in ['q', 'Q']:
                break

            tree = parser.parse(lexer.stream(s))
            tree = builder.build(tree)
            tree, exclusion = simplifier.canonicalize(tree)

            print('Representation: {}'.format(tree))
            print(' - LaTeX: {}'.format(latex.generate(tree)))
            plotter.plot(tree, exclusion, 'x', (-10, 10))

            deriv, de_ex = calculator.derivate(tree, exclusion, 'x')
            print('Derivative: {}'.format(deriv))
            print(' - LaTeX: {}'.format(latex.generate(deriv)))
            plotter.plot(deriv, de_ex, 'x', (-10, 10))

        print('Goodbye!')


if __name__ == "__main__":
    main(gui=True)
    # main()
    # lexer, parser, builder, simplifier, calculator, plotter, latex

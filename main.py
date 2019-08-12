import mathlib


def main():
    lexer = mathlib.Lexer(mathlib.default_lexer_grammar)
    parser = mathlib.Parser(mathlib.default_parser_grammar, lexer)

    builder = mathlib.NodeBuilder()
    simplifier = mathlib.NodeSimplifier()
    calculator = mathlib.Calculator(simplifier)
    plotter = mathlib.Plotter()

    print(mathlib.manual())
    while True:
        s = input('>>> ')
        if s.strip() in ['q', 'Q']:
            break

        tree = parser.parse(lexer.stream(s))
        tree = builder.build(tree)
        tree, exclusion = simplifier.canonicalize(tree)

        print('Representation: {}'.format(tree))
        plotter.plot(tree, exclusion, 'x', (-10, 10))

        deriv, de_ex = calculator.derivate(tree, exclusion, 'x')
        print('Derivative: {}'.format(deriv))
        plotter.plot(deriv, de_ex, 'x', (-10, 10))

    print('Goodbye!')


if __name__ == "__main__":
    main()

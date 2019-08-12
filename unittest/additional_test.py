import unittest

from mathlib.utils.test_util import *


class NotationTest(unittest.TestCase):
    def test_1(self):
        s = '(x-1)/(x-2)'
        notation_test(s)
        calculation_test(s, x=3)
        calculation_test(s, x=2)
        derivation_test(s, 'x')
        plot_test(s, 'x', (-5, 5))

    def test_2(self):
        s = '1/(1/x)'
        notation_test(s)
        calculation_test(s, x=0)
        derivation_test(s, 'x')

    def test_3(self):
        s = '1/(1/(1/(3+x)))'
        notation_test(s)
        calculation_test(s, x=1)
        calculation_test(s, x=-3)
        derivation_test(s, 'x')

    def test_4(self):
        s = 'log2_(2^(x+1))'
        notation_test(s)
        calculation_test(s, x=0)
        calculation_test(s, x=-10)
        derivation_test(s, 'x')

    def test_5(self):
        s = 'x^2*(x-1)^3*y/(y^2*(x-1))'
        notation_test(s)
        calculation_test(s, x=2, y=3)
        calculation_test(s, x=0, y=0)
        calculation_test(s, x=1, y=1)
        derivation_test(s, 'x')
        derivation_test(s, 'y')

    def test_6(self):
        s = '1/sin(x)'
        notation_test(s)
        calculation_test(s, x=math.pi/2)
        calculation_test(s, x=0)
        derivation_test(s, 'x')
        plot_test(s, 'x', (-10, 10))

    # def test_7(self):
    #     notation_test('x^(-3.5) + 1/x^3.5')
    #
    # def test_8(self):
    #     notation_test('(x-y)^2 + (sinx)^2 - logy_x')
    #
    # def test_9(self):
    #     notation_test('x^y * x^z * x^2')
    #
    # def test_10(self):
    #     notation_test('-3*x^2 + 5*x - 1 + 4*x^2 - x + 10')


if __name__ == '__main__':
    unittest.main()

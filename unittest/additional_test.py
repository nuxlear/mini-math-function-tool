import unittest

from mathlib.utils.test_util import *


class NotationTest(unittest.TestCase):
    def test_1(self):
        notation_test('(x-1)/(x-2)')

    def test_2(self):
        notation_test('1/(1/x)')

    def test_3(self):
        notation_test('1/(1/(1/(3+x)))')

    def test_4(self):
        notation_test('log2_(2^(x+1))')

    def test_5(self):
        notation_test('x^2*(x-1)^3*y/(y^2*(x-1))')

    # def test_6(self):
    #     notation_test('sin(cos(x/pi))')
    #
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

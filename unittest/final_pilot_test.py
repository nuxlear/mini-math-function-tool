import unittest

from mathlib.utils.test_util import *


class NotationTest(unittest.TestCase):
    def test_1(self):
        notation_test('x^99999*sinx/(x^99998)')

    def test_2(self):
        notation_test('3*x^2*log(e)_(e^x) - x^3 + x^2 - 7*x + 5')

    def test_3(self):
        notation_test('log(x)_(x^2)')

    def test_4(self):
        notation_test('x^(-3.5) + 1/x^3.5')

    def test_5(self):
        notation_test('sin(cos(x/pi))')

    def test_6(self):
        notation_test('x*tany + y^(2*z^2)')

    def test_7(self):
        notation_test('(x^y * x^z * x^(-2))^0.5')

    def test_8(self):
        notation_test('x/(x-1)*x/(x-2)')

    def test_9(self):
        notation_test('(x-y)^2 + sinx*sinx - logy_x')

    def test_10(self):
        notation_test('e^loge_x/((x-1)/(x+1))')


if __name__ == '__main__':
    unittest.main()

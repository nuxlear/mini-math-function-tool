import unittest

from mathlib.utils.test_util import *


class NotationTest(unittest.TestCase):
    def test_1(self):
        s = 'x^99999*sinx/(x^99998)'
        notation_test(s)
        calculation_test(s, x=3*math.pi/2)
        calculation_test(s, x=0)
        derivation_test(s, 'x')

    def test_2(self):
        s = '3*x^2*log(e)_(e^x) - x^3 + x^2 - 7*x + 5'
        notation_test(s)
        calculation_test(s, x=3)
        calculation_test(s, x=-4)
        derivation_test(s, 'x')

    def test_3(self):
        s = 'log(x)_(x^2)'
        notation_test(s)
        calculation_test(s, x=10)
        calculation_test(s, x=1)
        derivation_test(s, 'x')

    def test_4(self):
        s = 'x^(-3.5) + 1/x^3.5'
        notation_test(s)
        calculation_test(s, x=5)
        calculation_test(s, x=-1)
        derivation_test(s, 'x')

    def test_5(self):
        s = 'sin(cos(x/pi))'
        notation_test(s)
        calculation_test(s, x=3)
        derivation_test(s, 'x')

    def test_6(self):
        s = 'x*tany + y^(2*z^2)'
        notation_test(s)
        calculation_test(s, x=1, y=3, z=-1)
        calculation_test(s, x=4, y=math.pi/2, z=0)
        derivation_test(s, 'x')
        derivation_test(s, 'y')

    def test_7(self):
        s = '(x^y * x^z * x^(-2))^0.5'
        notation_test(s)
        calculation_test(s, x=7, y=3, z=0)
        calculation_test(s, x=4, y=-1, z=1)
        calculation_test(s, x=-2, y=3, z=1)
        derivation_test(s, 'x')
        derivation_test(s, 'y')

    def test_8(self):
        s = 'x/(x-1)*x/(x-2)'
        notation_test(s)
        calculation_test(s, x=-1)
        calculation_test(s, x=1)
        calculation_test(s, x=2)
        derivation_test(s, 'x')

    def test_9(self):
        s = '(x-y)^2 + sinx*sinx - logy_x'
        notation_test(s)
        calculation_test(s, x=math.pi/2, y=math.pi/4)
        calculation_test(s, x=0, y=4)
        calculation_test(s, x=8, y=3)
        derivation_test(s, 'x')
        derivation_test(s, 'y')

    def test_10(self):
        s = 'e^loge_x/((x-1)/(x+1))'
        notation_test(s)
        calculation_test(s, x=2)
        calculation_test(s, x=1)
        calculation_test(s, x=0)
        calculation_test(s, x=-1)
        derivation_test(s, 'x')


if __name__ == '__main__':
    unittest.main()

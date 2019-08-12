import unittest

from mathlib.utils.test_util import *


class NotationTest(unittest.TestCase):
    def test_1(self):
        s = 'x^2 + 3*y^2 - 64'
        notation_test(s)
        calculation_test(s, x=1, y=2)
        derivation_test(s, 'x')

    def test_2(self):
        s = '-x^3 + (x-1)^2 - 5*x +2 - (-1)/x'
        notation_test(s)
        calculation_test(s, x=1)
        derivation_test(s, 'x')

    def test_3(self):
        s = 'x * sinx + sinx^2'
        notation_test(s)
        calculation_test(s, x=math.pi/4)
        derivation_test(s, 'x')

    def test_4(self):
        s = 'log2_((x-1)^2) - tan((x-1)^2)'
        notation_test(s)
        calculation_test(s, x=5)
        calculation_test(s, x=1)
        derivation_test(s, 'x')

    def test_5(self):
        s = '(x-y+z)^0.2'
        notation_test(s)
        calculation_test(s, x=1, y=2, z=10)
        # TODO: fix parse bug
        calculation_test(s, x=1, y=2, z=-1)
        derivation_test(s, 'x')
        derivation_test(s, 'y')

    def test_6(self):
        s = 'sin(cos(x/pi))'
        notation_test(s)
        calculation_test(s, x=math.pi ** 2)
        derivation_test(s, 'x')

    def test_7(self):
        s = 'x^(-3.5) + 1/x^3.5'
        notation_test(s)
        calculation_test(s, x=4)
        calculation_test(s, x=0)
        derivation_test(s, 'x')

    def test_8(self):
        s = '(x-y)^2 + (sinx)^2 - logy_x'
        notation_test(s)
        calculation_test(s, x=10, y=5)
        calculation_test(s, x=math.pi/6, y=0.1)
        calculation_test(s, x=2, y=1)
        derivation_test(s, 'x')
        derivation_test(s, 'y')

    def test_9(self):
        s = 'x^y * x^z * x^2'
        notation_test(s)
        calculation_test(s, x=1, y=3, z=2)
        calculation_test(s, x=-1, y=-2, z=0)
        calculation_test(s, x=-2, y=0.3, z=-1.2)
        calculation_test(s, x=9, y=-2, z=0.5)
        derivation_test(s, 'x')
        derivation_test(s, 'z')

    def test_10(self):
        s = '-3*x^2 + 5*x - 1 + 4*x^2 - x + 10'
        notation_test(s)
        calculation_test(s, x=2)
        calculation_test(s, x=-1)
        derivation_test(s, 'x')


if __name__ == '__main__':
    unittest.main()

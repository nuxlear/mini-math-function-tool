from mathlib.core.calculator import *
from mathlib.io.latex import *

import matplotlib.pyplot as plt
import numpy as np


class Plotter:

    def __init__(self, calculator: Calculator=None):
        self.threshold = 10
        self.calculator = calculator

        # plt.ion()
        # self.fig, self.ax = plt.subplots()
        # plt.show(blocking=True)

        if calculator is None:
            self.calculator = Calculator()

    def plot(self, node: MathNode, exclusion: list, var: str, lim: tuple, **kwargs):
        l, r = lim
        if l.__class__ not in [int, float] or r.__class__ not in [int, float] \
                or l >= r:
            raise ValueError('invalid range: ({}, {})'.format(l, r))
        scale = 3
        step = (r - l) / (10 ** scale)

        targets = [round(x, scale) for x in np.arange(l, r + step, step)]
        xs, ys = [], []
        for t in targets:
            kwargs[var] = t
            y = self.calculator.eval(node, exclusion, **kwargs)
            if len(ys) > 0 and abs(y - ys[-1]) > self.threshold:
                xs.append((t + xs[-1])/2)
                ys.append(math.nan)
            xs.append(t)
            ys.append(y)

        # self.ax.plot(xs, ys)
        # self.ax.set_ylim(-10, 10)
        # plt.draw()
        plt.plot(xs, ys)
        plt.ylim(-10, 10)
        plt.show()

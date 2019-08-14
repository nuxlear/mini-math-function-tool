from mathlib.core.calculator import *
from mathlib.io.latex import *

import matplotlib.pyplot as plt
import numpy as np


class Plotter:

    def __init__(self, calculator: Calculator=None):
        self.scale = 3
        self.threshold = 10
        self.calculator = calculator

        # plt.ion()
        # self.fig, self.ax = plt.subplots()
        # plt.show(blocking=True)

        if calculator is None:
            self.calculator = Calculator()

    def _get_points(self, node: MathNode, exclusion: list, var: str, lim: tuple, **kwargs):
        l, r = lim
        if l.__class__ not in [int, float] or r.__class__ not in [int, float] \
                or l >= r:
            raise ValueError('invalid range: ({}, {})'.format(l, r))
        step = (r - l) / (10 ** self.scale)
        targets = [round(x, self.scale) for x in np.arange(l, r + step, step)]
        xs, ys = [], []
        for t in targets:
            kwargs[var] = t
            y = self.calculator.eval(node, exclusion, **kwargs)
            if len(ys) > 0 and abs(y - ys[-1]) > self.threshold:
                xs.append((t + xs[-1]) / 2)
                ys.append(math.nan)
            xs.append(t)
            ys.append(y)

        return xs, ys

    def plot(self, node: MathNode, exclusion: list, var: str, lim: tuple, **kwargs):
        xs, ys = self._get_points(node, exclusion, var, lim)

        # self.ax.plot(xs, ys)
        # self.ax.set_ylim(-10, 10)
        # plt.draw()
        plt.plot(xs, ys)
        plt.ylim(-10, 10)
        plt.show()

    def draw_plot(self, node: MathNode, exclusion: list, var: str, lim: tuple,
                  label: str, fig=None, ax=None, **kwargs):
        xs, ys = self._get_points(node, exclusion, var, lim, **kwargs)

        if fig is None and ax is None:
            fig, ax = plt.subplots()
            ax.spines['left'].set_position('center')
            ax.spines['right'].set_color('none')
            ax.spines['bottom'].set_position('center')
            ax.spines['top'].set_color('none')
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)

        ax.plot(xs, ys, label=label, linewidth=2.0, zorder=3)
        ax.set_xlim(*lim)
        ax.set_ylim(*lim)
        ax.legend()

        return fig, ax



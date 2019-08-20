from mathlib.core.calculator import *
from mathlib.io.latex import *

import matplotlib.pyplot as plt
import numpy as np


class Plotter:

    def __init__(self, calculator: Calculator=None):
        self.scale = 3
        self.threshold = 1e3
        self.max_std = 1e6
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
                _scale = 1
                _step = step / (10 ** _scale)
                additions = [round(x, self.scale + _scale) for x in np.arange(xs[-1], t + _step, _step)]
                for a in additions:
                    kwargs[var] = a
                    _y = self.calculator.eval(node, exclusion, **kwargs)
                    if abs(_y - ys[-1]) > self.threshold:
                        xs.append((a + xs[-1]) / 2)
                        ys.append(math.nan)
                    xs.append(a)
                    ys.append(_y)
            xs.append(t)
            ys.append(y)

        return xs, ys

    def _get_ylim(self, values):
        values = sorted([x for x in values if x != math.inf and x is not math.nan])
        if len(values) == 0:
            return None
        std = np.clip(np.std(values), 0, self.max_std)
        alpha = 0.2
        r = alpha*std/self.max_std
        values = values[int(len(values)*r): int(len(values)*(1-r))]
        mean, std = np.mean(values), np.std(values)
        return mean - 2*std, mean + 2*std

    def plot(self, node: MathNode, exclusion: list, var: str, lim: tuple, **kwargs):
        xs, ys = self._get_points(node, exclusion, var, lim)
        ylim = self._get_ylim(ys)
        if ylim is None:
            ylim = lim

        plt.plot(xs, ys)
        plt.ylim(*ylim)
        plt.show()

    def draw_plot(self, node: MathNode, exclusion: list, var: str, lim: tuple,
                  label: str, fig=None, ax=None, values=None, **kwargs):
        xs, ys = self._get_points(node, exclusion, var, lim, **kwargs)

        if fig is None and ax is None:
            fig, ax = plt.subplots()
            ax.spines['left'].set_position('zero')
            ax.spines['right'].set_color('none')
            ax.spines['bottom'].set_position('zero')
            ax.spines['top'].set_color('none')
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)

        ax.plot(xs, ys, label=label, linewidth=2.0, zorder=3)
        ax.set_xlim(*lim)

        ylim = self._get_ylim(ys)
        if ylim is None or ylim[0] == ylim[1]:
            ylim = lim

        if values is not None:
            _ylim = self._get_ylim(values)
            ylim = max(ylim[0], _ylim[0]), min(ylim[1], _ylim[1])

        ax.set_ylim(*ylim)
        ax.legend()

        return fig, ax, ys



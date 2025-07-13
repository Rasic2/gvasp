import logging
from functools import wraps

import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate

from gvasp.common.descriptor import ValueDescriptor

logger = logging.getLogger(__name__)


def plot_wrapper(type="default"):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kargs):
            plt.rc('font', family=self.family, weight=self.weight)  # set the font globally
            plt.rcParams['mathtext.default'] = 'regular'  # set the math-font globally
            plt.rcParams['lines.linewidth'] = self.linewidth  # set line-width
            plt.rcParams['lines.markersize'] = 2.0
            plt.tick_params(width=self.twidth, length=self.tlength)
            func(self, *args, **kargs)
            ax = plt.gca()
            ax.spines['bottom'].set_linewidth(self.bwidth)  # set border
            ax.spines['left'].set_linewidth(self.bwidth)
            ax.spines['top'].set_linewidth(self.bwidth)
            ax.spines['right'].set_linewidth(self.bwidth)
            try:
                plt.ticklabel_format(useOffset=False, style="plain")
            except:
                pass
            plt.xlim() if self.xlim is None else plt.xlim(self.xlim)
            plt.ylim() if self.ylim is None else plt.ylim(self.ylim)
            self.fontsize = self.fontsize * self.fontsize / 20 * max(min(self.width, self.height), 6) / 6
            if type == "PlotBand":
                if len(self.xticks) != len(self.pticks):
                    logger.warning(f"Specified High SYMM Points aren't included, use default...")
                else:
                    plt.xticks(ticks=self.kcoord, labels=self.xticks, fontsize=self.fontsize)
            else:
                plt.xticks(ticks=None if self.xticks is None else range(1, 2 * len(self.xticks), 2), labels=self.xticks,
                           fontsize=self.fontsize)
            plt.yticks(fontsize=self.fontsize)
            plt.xlabel(self.xlabel, fontdict={"weight": self.weight, "size": self.fontsize + 1})
            plt.ylabel(self.ylabel, fontdict={"weight": self.weight, "size": self.fontsize + 1})

            legends = plt.gca().axes.get_legend_handles_labels()
            if len(legends[0]):
                plt.legend(loc=self.lloc, fontsize=self.fontsize - 4, frameon=False)

            plt.title(self.title, fontsize=self.fontsize + 2)

        return wrapper

    # 直接传递了函数（没有调用装饰器）
    if callable(type):
        return decorator(type)

    return decorator


class Figure(object):
    """
    Plot-type class' parent, unify the figure format
    """
    lloc = ValueDescriptor("lloc",
                           ['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left',
                            'center right', 'lower center', 'upper center', 'center'])

    def __new__(cls, *args, **kwargs):
        if cls is Figure:
            raise TypeError(f"<{cls.__name__} class> may not be instantiated")
        return super(Figure, cls).__new__(cls)

    def __init__(self, width=8, height=6, family='Arial', weight='regular', fontsize=20, title='', xlim=None, ylim=None,
                 xticks=None, xlabel=None, ylabel=None, bwidth=1, linewidth=2, twidth=2, tlength=5, lloc="best",
                 **kargs):
        self.width = width
        self.height = height
        plt.close(1)  # close the old figure
        self.fig = plt.figure(figsize=(width, height))
        self.family = family
        self.weight = weight
        self.fontsize = fontsize
        self.title = title
        self.xlim = xlim
        self.ylim = ylim
        self.xticks = xticks
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.bwidth = bwidth
        self.linewidth = linewidth
        self.twidth = twidth  # tick_width
        self.tlength = tlength  # tick_length
        self.lloc = lloc  # legend_loc

    @staticmethod
    def show():
        plt.subplots_adjust(right=0.95, top=0.95)
        plt.show()

    @staticmethod
    def save(name="figure.svg"):
        plt.savefig(name, bbox_inches="tight")


class LineBase(object):
    """Line-Base-class, cant' instantiated"""

    def __new__(cls, *args, **kwargs):
        if cls is LineBase:
            raise TypeError(f"<{cls.__name__} class> may not be instantiated")
        return super(LineBase, cls).__new__(cls)

    def __init__(self, x, y, color, linewidth='', linestyle='-'):
        self.x = x
        self.y = y
        self.color = color
        self.linewidth = linewidth
        self.linestyle = linestyle

    def __call__(self):
        self.plot()

    def plot(self):
        plt.plot(self.x, self.y, self.linestyle, color=self.color, linewidth=self.linewidth)


class SolidLine(LineBase):
    """
    Solid Line class, subclass of LineBase
    """

    def __init__(self, linewidth=5, **kargs):
        super().__init__(linewidth=linewidth, **kargs)


class DashLine(LineBase):
    """Dash Line class, subclass of LineBase"""

    def __init__(self, linewidth=2, linestyle='--', **kargs):
        super().__init__(linewidth=linewidth, linestyle=linestyle, **kargs)


class PchipLine(LineBase):
    def __init__(self, linewidth=1, num=100, **kargs):
        super(PchipLine, self).__init__(linewidth=linewidth, **kargs)
        self.x_ori = self.x
        self.y_ori = self.y
        self.num = num
        self.x, self.y = PchipLine.interpolate(self.x_ori, self.y_ori, self.num)

    @staticmethod
    def interpolate(x_ori, y_ori, num):
        f = interpolate.PchipInterpolator(np.array(x_ori), np.array(y_ori))
        x_new = np.linspace(x_ori[0], x_ori[-1], num=num)
        y_new = f(x_new)
        return x_new, y_new


class Text(object):
    """
    Add text on the figure, for PlotPES.

    param:
        figure: Figure instance
        x:      bi-tuple, specify which x-range to add text
        y:      bi-tuple, specify which y-range to add text;
        text:   content
    """

    def __init__(self, figure, x, y, s, color, fontsize=18):
        self.figure = figure
        self.plt_figure = plt.gca().get_figure()
        self.renderer = self.plt_figure.canvas.get_renderer()
        self.x = x
        self.y = y
        self.s = s
        self.x_ave = sum(x) / 2
        self.y_ave = sum(y) / 2
        self.color = color
        self.fontsize = fontsize
        self.text = plt.text(self.x_ave, self.y_ave, self.s, ha='center', va='center', fontsize=self.fontsize,
                             color=self.color)
        self.text_box = self.text.get_window_extent(self.renderer)
        self.check_overlap()
        self.tailor_text()

    def check_overlap(self):
        """
        check the text overlap

        main idea:
            1. tailor box along the line
            2. if not, tailor the box vertically, then loop
        """
        left_m = -0.3 * (self.fontsize / 18) * (self.figure.width / 15.6) * (self.figure.height / 8)  # left margin
        right_m = 0.3 * (self.fontsize / 18) * (self.figure.width / 15.6) * (self.figure.height / 8)  # right margin
        top_m = 0.07 * (self.fontsize / 18) * (self.figure.width / 15.6) * (self.figure.height / 8)  # top margin
        bottom_m = -0.05 * (self.fontsize / 18) * (self.figure.width / 15.6) * (self.figure.height / 8)  # bottom margin
        color_plotted = list(self.figure.texts.keys())
        index_color = color_plotted.index(self.color)
        if index_color:  # not first line, index_color > 0
            limit_range = (self.x_ave + right_m < self.x[1] and self.x_ave + left_m > self.x[0])  # lines' range
            slide_along_k = 1
            slide_vertical = 1
            while limit_range:
                overlap = False
                for i in range(index_color):  # texts belonging to plotted lines before
                    values = [test.x_ave for test in self.figure.texts[color_plotted[i]]]  # all texts.x_ave values
                    if self.x_ave in values:  # x_ave in current range
                        index_fragment = values.index(self.x_ave)  # record index for x_ave
                        item = self.figure.texts[color_plotted[i]][index_fragment]  # obtain text object from index
                    else:
                        continue
                    overlap_cond_y = (self.y_ave + bottom_m < item.y_ave + top_m) and \
                                     (self.y_ave + bottom_m > item.y_ave + bottom_m) or \
                                     (self.y_ave + top_m > item.y_ave + bottom_m) and \
                                     (self.y_ave + top_m < item.y_ave + top_m)  # check y_direction overlap
                    overlap_cond_x = (self.x_ave + right_m > item.x_ave + left_m) and \
                                     (self.x_ave + right_m < item.x_ave + right_m) or \
                                     (self.x_ave + left_m < item.x_ave + right_m) and \
                                     (self.x_ave + left_m < item.x_ave + left_m)  # check x_direction overlap

                    cur_overlap = (overlap_cond_y or overlap_cond_x)  # check current line's overlap
                    if cur_overlap:
                        overlap = overlap or cur_overlap  # merge to all lines' overlap
                        break
                if not overlap:
                    break
                else:
                    k = (self.y[1] - self.y[0]) / (self.x[1] - self.x[0])  # slope of line
                    delta_y = (top_m - bottom_m) / 2 * slide_along_k * (-1) ** slide_along_k  # jump's distance
                    self.y_ave = self.y_ave + delta_y
                    self.x_ave = self.x_ave + delta_y / k
                    slide_along_k += 1
                    limit_range = (self.x_ave + right_m < self.x[1] and self.x_ave + left_m > self.x[0])  # check range

                if not limit_range:
                    slide_vertical += 1
                    slide_along_k = 1  # pull the text to original x_ave
                    self.x_ave = sum(self.x) / 2
                    self.y_ave = sum(self.y) / 2 + (top_m - bottom_m) / 100 * slide_vertical * (-1) ** slide_vertical
                    limit_range = (self.x_ave + right_m < self.x[1] and self.x_ave + left_m > self.x[0])
                    logger.debug(f"{self.x}: Adjust the intercept {slide_vertical - 1} times")

    def tailor_text(self):
        self.text.set_position((self.x_ave, self.y_ave))
        self.text_box = self.text.get_window_extent(self.renderer)

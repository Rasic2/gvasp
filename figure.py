from functools import wraps

from matplotlib import pyplot as plt, cycler

from logger import logger

COLOR = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']


def plot_wrapper(func):
    @wraps(func)
    def wrapper(self, *args, color=None, **kargs):
        plt.rc('font', family=self.family, weight=self.weight)  # set the font globally
        plt.rcParams['mathtext.default'] = 'regular'  # set the math-font globally
        plt.rcParams['lines.linewidth'] = 2  # set line-width
        plt.rcParams['axes.prop_cycle'] = cycler('color', COLOR) if color is None else cycler('color', color)
        func(self, *args, **kargs)
        ax = plt.gca()
        ax.spines['bottom'].set_linewidth(self.bwidth)  # set border
        ax.spines['left'].set_linewidth(self.bwidth)
        ax.spines['top'].set_linewidth(self.bwidth)
        ax.spines['right'].set_linewidth(self.bwidth)

        plt.xlim() if self.xlim is None else plt.xlim(self.xlim)
        plt.xticks(ticks=None if self.xticks is None else range(1, 2 * len(self.xticks), 2), labels=self.xticks,
                   fontsize=self.fontsize)
        plt.yticks(fontsize=self.fontsize)
        plt.xlabel(self.xlabel, fontsize=self.fontsize + 1)
        plt.ylabel(self.ylabel, fontsize=self.fontsize + 1)
        plt.title(self.title, fontsize=self.fontsize + 2)

    return wrapper


class Figure(object):
    def __new__(cls, *args, **kwargs):
        if cls is Figure:
            raise TypeError(f"<{cls.__name__} class> may not be instantiated")
        return super(Figure, cls).__new__(cls)

    def __init__(self, width=16, height=9, family='Arial', weight='bold', fontsize=20, title='', xlim=None,
                 xticks=None, xlabel=None, ylabel=None, bwidth=1):
        self.width = width
        self.height = height
        self.fig = plt.figure(figsize=(width, height))
        self.family = family
        self.weight = weight
        self.fontsize = fontsize
        self.title = title
        self.xlim = xlim
        self.xticks = xticks
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.bwidth = bwidth

    @staticmethod
    def show():
        plt.show()

    @staticmethod
    def save(name="figure.svg"):
        plt.savefig(name)


class LineBase(object):
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
    def __init__(self, linewidth=5, **kargs):
        super().__init__(linewidth=linewidth, **kargs)


class DashLine(LineBase):
    def __init__(self, linewidth=2, linestyle='--', **kargs):
        super().__init__(linewidth=linewidth, linestyle=linestyle, **kargs)


class Text(object):
    def __init__(self, figure, x, y, text, color, fontsize=18):
        self.figure = figure
        self.x = x
        self.y = y
        self.x_ave = sum(x) / 2
        self.y_ave = sum(y) / 2
        self.color = color
        self.fontsize = fontsize
        self.text = text
        self.check_overlap()
        self.plot_text()

    def check_overlap(self):
        left_m = -0.3 * (self.fontsize / 18) / (self.figure.width / 15.6) / (self.figure.height / 8)  # left margin
        right_m = 0.3 * (self.fontsize / 18) / (self.figure.width / 15.6) / (self.figure.height / 8)  # right margin
        top_m = 0.07 * (self.fontsize / 18) / (self.figure.width / 15.6) / (self.figure.height / 8)  # top margin
        bottom_m = -0.05 * (self.fontsize / 18) / (self.figure.width / 15.6) / (self.figure.height / 8)  # bottom margin
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
                    overlap_cond_y = (self.y_ave + bottom_m > item.y_ave + top_m or
                                      self.y_ave + top_m < item.y_ave + bottom_m)  # check y_direction overlap
                    overlap_cond_x = (self.x_ave + right_m < item.x_ave + left_m or
                                      self.x_ave + left_m > item.x_ave + right_m)  # check x_direction overlap
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
                    logger.info(f"{self.x}: Adjust the intercept {slide_vertical - 1} times")

    def plot_text(self):
        plt.text(self.x_ave, self.y_ave, self.text, ha='center', va='center', fontsize=self.fontsize, color=self.color)

from common.plot import PlotOpt


def plot():
    outcar = PlotOpt("OUTCAR_freq")
    outcar.plot()
    outcar.show()


if __name__ == '__main__':
    plot()

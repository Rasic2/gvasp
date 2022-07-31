import matplotlib.pyplot as plt

from common.file import OUTCAR


def bandgap():
    outcar = OUTCAR("OUTCAR")
    return outcar.bandgap()


def animation_freq():
    outcar = OUTCAR("OUTCAR")
    outcar.animation_freq()


def plot():
    outcar = OUTCAR("OUTCAR_freq")
    outcar.plot()
    outcar.show()


if __name__ == '__main__':
    plot()

from common.file import OUTCAR


def bandgap():
    outcar = OUTCAR("OUTCAR")
    return outcar.bandgap()


def animation_freq():
    outcar = OUTCAR("OUTCAR")
    outcar.animation_freq()


if __name__ == '__main__':
    animation_freq()

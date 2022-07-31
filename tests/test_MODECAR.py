from common.file import MODECAR


def test_from_freq():
    MODECAR.write_from_freq(freq=0, scale=0.5)


def test_from_POSCAR():
    MODECAR.write_from_POSCAR(pos1="POSCAR_IS_sort", pos2="POSCAR_FS_sort")


test_from_POSCAR()

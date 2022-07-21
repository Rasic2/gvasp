import time

from file import CHGCAR_tot, CHGCAR_mag, CHGCAR, AECCAR0, AECCAR2

# chg_tot = CHGCAR_tot("CHGCAR_tot")
# chg_tot.load()
#
# chg_mag = CHGCAR_mag("CHGCAR_mag")
# chg_mag.load()
#
# chg = CHGCAR("CHGCAR")
# chg.split()
if __name__ == '__main__':
    file0 = AECCAR0("AECCAR0")
    file2 = AECCAR2("AECCAR2")
    chgcar_sum = file0 + file2
    chgcar_sum.write()
    print()

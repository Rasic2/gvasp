from QVasp.common.file import CHGCAR_mag

# chg_tot = CHGCAR_tot("CHGCAR_tot")
# chg_tot.load()
#

#
# chg = CHGCAR("CHGCAR")
# chg.split()
if __name__ == '__main__':
    # file0 = AECCAR0("AECCAR0")
    # file2 = AECCAR2("AECCAR2")
    # chgcar_sum = file0 + file2
    # print(file0.NGX)
    # chgcar_sum.write()
    # print(time.time())
    chg_mag = CHGCAR_mag("CHGCAR_mag")
    # chg_mag = AECCAR2("AECCAR2")
    # chg_mag.load()
    # print(time.time())
    CHGCAR_mag.to_grd(name="vasp.grd", DenCut=250)
    print()

from file import CHGCAR_tot, CHGCAR_mag, CHGCAR

chg_tot = CHGCAR_tot("CHGCAR_tot")
chg_tot.load()

chg_mag = CHGCAR_mag("CHGCAR_mag")
chg_mag.load()

chg = CHGCAR("CHGCAR")
chg.split()
print()

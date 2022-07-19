import time

import numpy as np
from file import DOSCAR
print(time.time())
dos_instance = DOSCAR("DOSCAR-test")
NAtom = dos_instance.NAtom
NDOS = dos_instance.NDOS
fermi = dos_instance.fermi
TDOS = np.array(dos_instance.strings[6:6 + NDOS])
TDOS = np.array(np.char.split(TDOS).tolist()).astype(float)
energy_list, TDOS_up, TDOS_down = TDOS[:, 0] - fermi, TDOS[:, 1], -TDOS[:, 2]

index = (NDOS + 1) * np.array(range(1, NAtom + 1)) + 6

LDOS = []
for sub, i in enumerate(index):
    lDOS = np.array(dos_instance.strings[i:i+NDOS])
    lDOS = np.array(np.char.split(lDOS).tolist()).astype(float)
    LDOS.append(lDOS)
LDOS = np.array(LDOS)
print(time.time())
print()

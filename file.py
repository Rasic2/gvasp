import math
from multiprocessing import Pool as ProcessPool
from pathlib import Path

import numpy as np
from pandas import DataFrame

from CLib import _dos
from error import StructureNotEqualError, GridNotEqualError
from logger import logger
from structure import Structure


class VASPFile(object):

    def __new__(cls, *args, **kwargs):
        if cls.__base__ is object:
            raise TypeError(f"<{cls.__name__} class> may not be instantiated")
        return super(VASPFile, cls).__new__(cls)

    def __init__(self, name):
        self.name = name
        self._strings = None

    # def __repr__(self):
    #     return f"<{self.ftype} '{self.fname}'>"

    @property
    def type(self):
        return self.__class__.__name__

    @property
    def strings(self):
        if self._strings is None:
            with open(self.name, "r") as f:
                self._strings = f.readlines()
        return self._strings


class POSCAR(VASPFile):

    def __init__(self, name):
        super().__init__(name=name)

    def __getitem__(self, index):
        return self.strings[index]

    # def __sub__(self, other):
    #     self.structure = self.to_structure()
    #     other.structure = other.to_structure()
    #     if np.all(self.structure.lattice.matrix == other.structure.lattice.matrix):
    #         return self.structure - other.structure
    #     else:
    #         raise ArithmeticError(f"{self} and {other} not have the same lattice vector!")
    #
    @property
    def structure(self):
        return Structure.from_POSCAR(self.name)


class CONTCAR(POSCAR):
    def __init__(self, name):
        super().__init__(name=name)


#
#
# class XDATCAR(VASPFile):
#     def __init__(self, name, **kargs):
#         super().__init__(name)
#
#         self.kargs = kargs
#         self.system = self.strings[0].rstrip()
#         self.factor = self.strings[1].rstrip()
#         self.lattice = Lattice.from_string(self.strings[2:5])
#         element_name = self.strings[5].split()
#         element_count = [int(item) for item in self.strings[6].split()]
#         self.element = sum([[name] * count for name, count in zip(element_name, element_count)], [])
#         self.frames = [i for i in range(len(self.strings)) if self.strings[i].find("Direct") != -1]
#
#         self._structures = []
#
#     def __len__(self):
#         return len(self.frames)
#
#     def __getitem__(self, index):
#         return self.structures[index]
#
#     @property
#     def structures(self):
#         if len(self._structures) == 0:
#             for frame in self.frames:
#                 frac_coord = np.array([[float(item) for item in line.split()] for line in
#                                        self.strings[frame + 1:frame + 1 + len(self.element)]])
#                 atoms = Atoms(formula=self.element, frac_coord=frac_coord)
#                 self._structures.append(Structure(atoms=atoms, lattice=self.lattice, **self.kargs))
#         return self._structures
#
#     def split_file(self, index, fname, system=None, factor=1., num_workers=4):
#         if isinstance(index, int):
#             self[index].to_POSCAR(fname=fname, system=system, factor=factor)
#         elif isinstance(index, (Iterable, slice)):
#             pool = ProcessPool(processes=num_workers)
#             for index_i, fname_i in zip(index, fname):
#                 pool.apply_async(self[index_i].to_POSCAR, args=(fname_i, system, factor))
#             pool.close()
#             pool.join()

class DOSCAR(VASPFile):
    def __init__(self, name):
        super(DOSCAR, self).__init__(name=name)
        self.NAtom = int(self.strings[0].split()[0])
        self.Emax, self.Emin, self.NDOS, self.fermi = tuple(map(float, self.strings[5].split()[:4]))
        self.NDOS = int(self.NDOS)

    def load(self):
        ORBITALS = ['s', 'p', 'd', 'f']
        COLUMNS = ['s_up', 's_down', 'py_up', 'py_down', 'pz_up', 'pz_down', 'px_up', 'px_down', 'dxy_up', 'dxy_down',
                   'dyz_up', 'dyz_down', 'dz2_up', 'dz2_down', 'dxz_up', 'dxz_down', 'dx2_up', 'dx2_down', 'f1_up',
                   'f1_down', 'f2_up', 'f2_down', 'f3_up', 'f3_down', 'f4_up', 'f4_down', 'f5_up', 'f5_down', 'f6_up',
                   'f6_down', 'f7_up', 'f7_down']

        def merge_dos(energy_list, Total_up, Total_down, atom_list, length):
            """TODO:  need  optimize, deprecate DataFrame"""
            atom_data = [energy_list]
            columns = COLUMNS[:length]
            orbitals = ORBITALS[1:int(math.sqrt(length / 2))]
            Total_Dos = DataFrame(index=energy_list, columns=['tot_up', 'tot_down'], dtype='object')
            Total_Dos['tot_up'] = Total_up
            Total_Dos['tot_down'] = Total_down

            for data in atom_list:
                DATA = DataFrame(data, index=energy_list, columns=columns)
                DATA['up'] = 0.0
                DATA['down'] = 0.0
                for orbital in orbitals:
                    DATA[orbital + '_up'] = 0.0
                    DATA[orbital + '_down'] = 0.0
                    orbital_p_up = [item for item in DATA.columns.values if
                                    item.startswith(orbital) and item.endswith('up') and item != '{}_up'.format(
                                        orbital) and item != 'up']
                    orbital_p_down = [item for item in DATA.columns.values if
                                      item.startswith(orbital) and item.endswith('down') and item != '{}_down'.format(
                                          orbital) and item != 'down']
                    for item in orbital_p_up:
                        DATA[f'{orbital}_up'] += DATA[item]
                    for item in orbital_p_down:
                        DATA[f'{orbital}_down'] += DATA[item]
                    DATA['up'] += DATA[f'{orbital}_up']
                    DATA['down'] += DATA[f'{orbital}_down']
                DATA['up'] += DATA['s_up']
                DATA['down'] += DATA['s_down']
                atom_data.append(DATA)

            self.TDOS = Total_Dos  # DataFrame(NDOS, 2)
            self.LDOS = atom_data  # energy + List(NAtom, NDOS, NOrbital+8)
            return self

        return merge_dos(*_dos.load(self.strings, self.NDOS, self.fermi))


class EIGENVAL(VASPFile):
    def __init__(self, name):
        super(EIGENVAL, self).__init__(name=name)
        self.NKPoint, self.NBand = tuple(map(int, self.strings[5].split()[1:]))
        self.KPoint_coord = None
        self.energy = None

    def load(self):
        """
        load Eigenval obtain the band-energy

        @return:
            self.energy:    shape=(NKPoint, NBand, 2)
        """
        self.KPoint_coord = []
        self.energy = []
        energy_flag = False
        sBand = []
        for index, line in enumerate(self.strings):
            if index % (self.NBand + 2) == 7:
                self.KPoint_coord.append(tuple(map(float, line.split()[0:3])))
                energy_flag = True
                continue
            elif energy_flag:
                sBand.append(list(map(float, line.split()[1:])))
                if len(sBand) == self.NBand:
                    energy_flag = False
                    self.energy.append(sBand)
                    sBand = []

        self.KPoint_coord = np.array(self.KPoint_coord)
        self.energy = np.array(self.energy)

        return self

    def write(self, directory='band_data'):
        """
        Write band-data to file, each band corresponding to one file and named as band_{index}

        @params:
            dir:    save directory, default: $CWD/band_data
        """
        Path(directory).mkdir(exist_ok=True)
        if getattr(self, "energy", None) is None:
            self.load()
        for index in range(self.NBand):
            np.savetxt(f"{directory}/band_{index + 1}", self.energy[:, index])
        logger.info(f"Band data has been saved to {directory} directory")


class CHGBase(CONTCAR):
    """
    Subclass of POSCAR, inherit <structure property>
    """

    def __new__(cls, *args, **kwargs):
        if cls is CHGBase:
            raise TypeError(f"<{cls.__name__} class> may not be instantiated")
        return super().__new__(cls)

    def __init__(self, name):
        super(CHGBase, self).__init__(name=name)
        self.NGX, self.NGY, self.NGZ = None, None, None
        self.density = None

    def __add__(self, other):
        if self.__class__.__name__.startswith("AECCAR") and other.__class__.__name__.startswith("AECCAR"):
            if self.density is None and other.density is None:
                pool = ProcessPool(processes=2)
                results = [pool.apply_async(self.load), pool.apply_async(other.load)]
                self, other = [item.get() for item in results]
                pool.close()
                pool.join()
            elif self.density is None:
                self.load()
            elif other.density is None:
                other.load()

            if self.structure != other.structure:
                raise StructureNotEqualError(f"{self.name}.structure is not equal to {other.name}.structure")
            if (self.NGX, self.NGY, self.NGZ) != (other.NGX, other.NGY, other.NGZ):
                raise GridNotEqualError(f"{self.name}.NGrid is not equal to {other.name}.NGrid")
            density_sum = self.density + other.density
            return CHGCAR_sum.from_array("CHGCAR_sum", self.structure, (self.NGX, self.NGY, self.NGZ), density_sum)
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: {self.__class__.__name__} and {other.__class__.__name__}")

    def load(self):
        """
        load Electronic-Density

        @return:
            self.density:    shape=(NGX, NGY, NGZ)
        """
        start = len(self.structure.atoms) + 9
        self.NGX, self.NGY, self.NGZ = tuple(map(int, self.strings[start].split()))
        self.density = np.append([], np.char.split(self.strings[start + 1:]).tolist()).astype(float)
        assert self.density.size == self.NGX * self.NGY * self.NGZ, "Load density failure, size is not consistent"
        self.density = self.density.reshape((self.NGX, self.NGY, self.NGZ), order="F")
        return self

    def write(self, system=None, factor=1.0):
        """
        write CHGCAR_* file from array

        @param:
            system:     specify the structure system
            factor:     coordination factor
        """
        self.structure.write(name=self.__class__.__name__, system=system, factor=factor)
        density_fortran = self.density.reshape(-1, order="F").reshape(-1, 5)
        with open(self.__class__.__name__, "a+") as f:
            f.write(f"{self.NGX:>5}{self.NGY:>5}{self.NGZ:>5}\n")
            np.savetxt(f, density_fortran, fmt="%18.11E")


class AECCAR0(CHGBase):
    def __init__(self, name):
        super(AECCAR0, self).__init__(name=name)


class AECCAR2(CHGBase):
    def __init__(self, name):
        super(AECCAR2, self).__init__(name=name)


class CHGCAR_sum(CHGBase):
    def __init__(self, name):
        super(CHGCAR_sum, self).__init__(name=name)
        self._structure = None

    @property
    def structure(self):
        if self._structure is None:
            self._structure = super(CHGCAR_sum, self).structure()
        return self._structure

    @structure.setter
    def structure(self, _structure):
        self._structure = _structure

    @staticmethod
    def from_array(name: str, structure, NGrid: tuple[int, int, int], density):
        instance = CHGCAR_sum(name=name)
        instance.structure = structure
        instance.NGX, instance.NGY, instance.NGZ = NGrid
        instance.density = density
        return instance


class CHGCAR_tot(CHGBase):
    def __init__(self, name):
        super(CHGCAR_tot, self).__init__(name=name)


class CHGCAR_mag(CHGBase):
    def __init__(self, name):
        super(CHGCAR_mag, self).__init__(name=name)


class CHGCAR(CONTCAR):
    def __init__(self, name):
        super(CHGCAR, self).__init__(name=name)
        self.NGX, self.NGY, self.NGZ, self.NGrid = None, None, None, None
        self.density_tot, self.density_mag = None, None

        self._head = None
        self._density_tot_strings, self._density_mag_strings = None, None

    def load(self):
        """
        load Electronic-Density

        @return:
            self.NGrid:                 NGX * NGY * NGZ
            self.density:               shape=(NGX, NGY, NGZ)
            self._density_strings:      density with strings format
        """
        start = len(self.structure.atoms) + 9
        self.NGX, self.NGY, self.NGZ = tuple(map(int, self.strings[start].split()))
        self._head = self.strings[:start + 1]
        index = np.where(np.array(self.strings) == self.strings[start])[0]
        assert len(index) == 2, f"Search indicator failure"

        self.NGrid = self.NGX * self.NGY * self.NGZ
        count = self.NGrid / 5 if self.NGrid % 5 == 0 else self.NGrid / 5 + 1
        count = int(count)

        self._density_tot_strings = self.strings[index[0] + 1:index[0] + 1 + count]
        self._density_mag_strings = self.strings[index[1] + 1:index[1] + 1 + count]

        self.density_tot = np.append([], np.char.split(self._density_tot_strings).tolist()).astype(float)
        self.density_tot = self.density_tot.reshape((self.NGX, self.NGY, self.NGZ), order="F")

        self.density_mag = np.append([], np.char.split(self._density_mag_strings).tolist()).astype(float)
        self.density_mag = self.density_mag.reshape((self.NGX, self.NGY, self.NGZ), order="F")

    def split(self):
        """split CHGCAR to CHGCAR_tot && CHGCAR_mag"""
        if getattr(self, "_head", None) is None:
            self.load()

        with open("CHGCAR_tot", "w") as tot, open("CHGCAR_mag") as mag:
            tot.writelines(self._head)
            tot.writelines(self._density_tot_strings)
            mag.writelines(self._head)
            mag.writelines(self._density_mag_strings)

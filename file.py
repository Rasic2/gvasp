import math
from collections import namedtuple
from datetime import datetime
from multiprocessing import Pool as ProcessPool
from pathlib import Path
from typing import List

import numpy as np
from pandas import DataFrame

from CLib import _dos, _file
from base import Atoms, Lattice
from error import StructureNotEqualError, GridNotEqualError, AnimationError, FrequencyError
from logger import logger
from structure import Structure


class MetaFile(object):

    def __new__(cls, *args, **kwargs):
        if cls.__base__ is object:
            raise TypeError(f"<{cls.__name__} class> may not be instantiated")
        return super(MetaFile, cls).__new__(cls)

    def __init__(self, name):
        self.name = name
        self._strings = None

    def __getitem__(self, index):
        return self.strings[index]

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


class ARCFile(MetaFile):
    @staticmethod
    def write(name: str, structure: List[Structure], lattice: Lattice):
        a, b, c = lattice.length
        alpha, beta, gamma = lattice.angle
        with open(name, "w") as f:
            f.write("!BIOSYM archive 3\n")
            f.write("PBC=ON\n")
            for frame in range(len(structure)):
                atoms = structure[frame].atoms.set_coord(lattice)
                f.write("Auto Generated CAR File\n")
                f.write(f'!DATE {datetime.now().strftime("%a %b %d %H:%M:%S  %Y")}\n')
                f.write(f"PBC   {a:.5f}  {b:.5f}  {c:.5f}  {alpha:.5f}  {beta:.5f}  {gamma:.5f} (P1)\n")
                for atom in atoms:
                    formula, order = atom.formula, atom.order
                    element = formula + str(order + 1)
                    x, y, z = atom.cart_coord
                    f.write(f"{element:5s} {x:14.10f} {y:14.10f} {z:14.10f} XXXX 1       xx     {formula:2s} 0.0000\n")
                f.write("end\n")
                f.write("end\n")


class POSCAR(MetaFile):

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
    pass


class XDATCAR(POSCAR):
    def __init__(self, name):
        super().__init__(name)

        self.lattice = Lattice.from_string(self.strings[2:5])
        element_name = self.strings[5].split()
        element_count = [int(item) for item in self.strings[6].split()]
        self.element = sum([[name] * count for name, count in zip(element_name, element_count)], [])
        self.frames = [i for i in range(len(self.strings)) if self.strings[i].find("Direct") != -1]
        self._structure = []

    @property
    def structure(self):
        if len(self._structure) == 0:
            for frame in self.frames:
                frac_coord = np.array([[float(item) for item in line.split()] for line in
                                       self.strings[frame + 1:frame + 1 + len(self.element)]])
                atoms = Atoms(formula=self.element, frac_coord=frac_coord)
                self._structure.append(Structure(atoms=atoms, lattice=self.lattice))
        return self._structure

    def to_arc(self, name):
        """Transform the XDATCAR to *.arc file"""
        ARCFile.write(name=name, structure=self.structure, lattice=self.lattice)


#     def __len__(self):
#         return len(self.frames)
#
#     def __getitem__(self, index):
#         return self.structures[index]

#     def split_file(self, index, fname, system=None, factor=1., num_workers=4):
#         if isinstance(index, int):
#             self[index].to_POSCAR(fname=fname, system=system, factor=factor)
#         elif isinstance(index, (Iterable, slice)):
#             pool = ProcessPool(processes=num_workers)
#             for index_i, fname_i in zip(index, fname):
#                 pool.apply_async(self[index_i].to_POSCAR, args=(fname_i, system, factor))
#             pool.close()
#             pool.join()

class DOSCAR(MetaFile):
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


class EIGENVAL(MetaFile):
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
                results = [pool.apply_async(self.load), pool.apply_async(other.load)]  # new instance
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
        info = _file.load(self.name)
        self.NGX, self.NGY, self.NGZ = info.NGX, info.NGY, info.NGZ
        self.density = info.density
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
    pass


class AECCAR2(CHGBase):
    pass


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
    pass


class CHGCAR_mag(CHGBase):
    @staticmethod
    def to_grd(name="vasp.grd", DenCut=-1):
        """
        transform CHGCAR_mag to *.grd file

        @param
            name:       specify the name of *.grd file
            DenCut:     density lower than DenCut will be set to zero;
                        default: -1, disable the DenCut option
        """
        _file.to_grd(name, DenCut)


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


class OUTCAR(MetaFile):
    def __init__(self, name):
        super(OUTCAR, self).__init__(name=name)
        element_name = [item.split()[3] for item in self.strings if item.find("TITEL") != -1]
        element_count = [list(map(int, item.split()[4:])) for item in self.strings if item.find("ions per") != -1][0]
        self.element = sum([[name] * count for name, count in zip(element_name, element_count)], [])
        self.lattice = {Lattice.from_string(self.strings[index + 1:index + 4]) for index, item in
                        enumerate(self.strings) if item.find("direct lattice vectors") != -1}
        self.lattice = list(self.lattice)[0] if len(self.lattice) == 1 else self.lattice
        self._frequency = [i for i in range(len(self.strings)) if self.strings[i].find("Hz") != -1]

        self.frequency = None
        if len(self._frequency):
            self.frequency = namedtuple("Frequency", ("image", "wave_number", "coord", "vibration"))
            self.parse_freq()

    def parse_freq(self):
        """
        Parse frequency information from OUTCAR

        @return:
            register self.frequency attr (type: namedtuple)
        """
        image, wave_number, coord, vibration = [], [], [], []
        for index in self._frequency:
            item = self.strings[index].split()
            image.append(False) if item[1] == "f" else image.append(True)
            wave_number.append(float(item[-4]))
            item = list(map(lambda x: [float(i) for i in x],
                            np.char.split(self.strings[index + 2:index + 2 + len(self.element)])))
            coord.append(np.array(item)[:, :3])
            vibration.append(np.array(item)[:, 3:])

        self.frequency.image = image
        self.frequency.wave_number = np.array(wave_number)
        self.frequency.coord = np.array(coord)
        self.frequency.vibration = np.array(vibration)

    def animation_freq(self, freq: [str, int] = "image", frames: int = 30, scale: float = 0.6):
        """
        Generate freq.arc file from OUTCAR

        @param:
            freq:       specify which freq you want to animate, accept [int, str] arguments
            frames:     specify how many points you want to interpolate along one direction, default = 30
            scale:      determine the vibration scale, default = 0.6
        """
        if self.frequency is None:
            raise AnimationError(f"{self.name} don't include frequency information")

        if isinstance(freq, int) and freq not in range(len(self._frequency)):
            raise FrequencyError(f"freq{freq} is not in {self.name}, should be {list(range(len(self._frequency)))}")

        if isinstance(freq, str) and freq != "image":
            raise FrequencyError(f"`{freq}` is not supported, should be `image`")

        freq = [index for index, item in enumerate(self.frequency.image) if item] if isinstance(freq, str) else freq

        # generate the directions for vibration
        direction_001 = np.linspace(start=0, stop=scale, num=frames)  # 0-1 direction
        direction_010 = np.linspace(start=scale, stop=0, num=frames)  # 1-0 direction
        direction_101 = np.linspace(start=0, stop=-scale, num=frames)  # 0-^1 direction
        direction_110 = np.linspace(start=-scale, stop=0, num=frames)  # ^1-0 direction
        direction_all = np.concatenate([direction_001, direction_010, direction_101, direction_110])
        direction_all = direction_all[:, np.newaxis, np.newaxis]

        # generate multi-frames new coordinates
        coord_freq = []
        for freq_index in freq:
            coord = np.repeat(self.frequency.coord[freq_index][np.newaxis, :], direction_all.shape[0], axis=0)
            vibration = np.repeat(self.frequency.vibration[freq_index][np.newaxis, :], direction_all.shape[0], axis=0)
            coord_freq.append(coord + vibration * direction_all)

        # generate the *.arc file
        if not isinstance(self.lattice, Lattice):
            raise NotImplementedError("we here only considered the lattice unchangeable for the whole calculation")

        for freq_index, coord_index in zip(freq, coord_freq):
            structure = [Structure(atoms=Atoms(formula=self.element, cart_coord=cart_coord), lattice=self.lattice)
                         for cart_coord in coord_index]
            ARCFile.write(name=f"freq{freq_index + 1}.arc", structure=structure, lattice=self.lattice)


class MODECAR(MetaFile):
    @staticmethod
    def write(freq: int, scale: float, outcar="OUTCAR"):
        outcar = OUTCAR(name=outcar)
        frequency = outcar.frequency.vibration[freq]
        np.savetxt("MODECAR", frequency * scale, fmt="%10.5f")

import math
from collections import namedtuple
from datetime import datetime
from functools import wraps, reduce
from multiprocessing import Pool as ProcessPool
from operator import add
from pathlib import Path
from typing import List

import numpy as np
from lxml import etree
from pandas import DataFrame

from gvasp.lib import dos_cython, file_bind
from gvasp.common.base import Atoms, Lattice
from gvasp.common.error import StructureNotEqualError, GridNotEqualError, AnimationError, FrequencyError, \
    AttributeNotRegisteredError, ParameterError, PotDirNotExistError
from gvasp.common.logger import Logger
from gvasp.common.parameter import Parameter
from gvasp.common.setting import RootDir
from gvasp.common.structure import Structure

POTENTIAL = ['PAW_LDA', 'PAW_PBE', 'PAW_PW91', 'USPP_LDA', 'USPP_PW91']
ORBITALS = ['s', 'p', 'd', 'f']
COLUMNS = ['s_up', 's_down', 'py_up', 'py_down', 'pz_up', 'pz_down', 'px_up', 'px_down', 'dxy_up', 'dxy_down',
           'dyz_up', 'dyz_down', 'dz2_up', 'dz2_down', 'dxz_up', 'dxz_down', 'dx2_up', 'dx2_down', 'f1_up',
           'f1_down', 'f2_up', 'f2_down', 'f3_up', 'f3_down', 'f4_up', 'f4_down', 'f5_up', 'f5_down', 'f6_up',
           'f6_down', 'f7_up', 'f7_down']


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

    def __repr__(self):
        return f"<{self.type} | name='{self.name}'>"

    @property
    def type(self):
        return self.__class__.__name__

    @property
    def strings(self):
        if self._strings is None:
            with open(self.name, "r") as f:
                self._strings = f.readlines()
        return self._strings


class StructInfoFile(MetaFile):

    def __new__(cls, *args, **kwargs):
        if cls is StructInfoFile:
            raise TypeError(f"<{cls.__name__} class> may not be instantiated")
        return super().__new__(cls)

    @property
    def structure(self):
        return Structure.from_POSCAR(self.name)


class CellFile(StructInfoFile):

    @property
    def structure(self):  # overwrite <structure method>
        return Structure.from_cell(self.name)

    def to_POSCAR(self):
        self.structure.write_POSCAR(name="POSCAR")


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


def formatter(parameters):
    """
    formatter wrapper: format the INCAR parameters

    @params:
        parameters:     which type of INCAR parameters
        func:           write* func in INCAR class
    """

    def func_wrapper(func):
        @wraps(func)
        def wrapper(self, name):

            # check if exist this type parameter
            for param in parameters:
                if param in self.__dict__.keys():
                    func(self, name)
                    break
            else:
                return

            # write parameter
            for param in parameters:
                if param in self.__dict__.keys():
                    if isinstance(self.__dict__[param], bool):
                        with open(name, "a+") as f:
                            f.write(f"  {param} = .{str(self.__dict__[param]).upper()}. \n")
                    elif param in ['LDAUL', 'LDAUU', 'LDAUJ']:
                        with open(name, "a+") as f:
                            f.write(f"  {param} = {'  '.join(list(map(str, self.__dict__[param])))} \n")
                    else:
                        with open(name, "a+") as f:
                            f.write(f"  {param} = {self.__dict__[param]} \n")

        return wrapper

    return func_wrapper


class INCAR(MetaFile, Parameter):

    def __init__(self, name):
        super(INCAR, self).__init__(name=name)
        self._init_attr()

    def __getattr__(self, item):
        if item in self.__dict__.keys():
            return self.__dict__[item]
        elif item in self.__class__.__dict__.keys():
            return self.__class__.__dict__[item]

    def _init_attr(self):
        """
        Initialize the attributes, if attribute not found, raise AttributeNotRegisteredError
        """
        for line in self.strings:
            if line.split()[0][0] != "#":
                real_line = line.split("#")[0]
                attr_name = real_line.split("=")[0].strip()
                attr_value = real_line.split("=")[1].strip()
                for param_type in INCAR._type_trans.keys():
                    if attr_name in INCAR._type_trans[param_type]['name']:
                        attr_value = INCAR._type_trans[param_type]['func'](attr_value)
                        break
                else:
                    raise AttributeNotRegisteredError(f"{attr_name} is not registered")
                setattr(self, attr_name, attr_value)

    def write(self, name):
        """
        Write interface, callback every _write* func
        """
        self._write_base(name)
        self._write_scf(name)
        self._write_opt(name)
        self._write_md(name)
        self._write_charge(name)
        self._write_density(name)
        self._write_freq(name)
        self._write_stm(name)
        self._write_vtst(name)
        self._write_neb(name)
        self._write_dimer(name)
        self._write_plusU(name)

    @formatter(Parameter._baseParam)
    def _write_base(self, name):
        with open(name, "w") as f:
            f.write(f"#----------/Base Parameter/----------# \n")

    @formatter(Parameter._scfParam)
    def _write_scf(self, name):
        with open(name, "a+") as f:
            f.write(f"#----------/SCF Parameter/----------# \n")

    @formatter(Parameter._optParam)
    def _write_opt(self, name):
        with open(name, "a+") as f:
            f.write(f"#----------/Optimize Parameter/----------# \n")

    @formatter(Parameter._mdParam)
    def _write_md(self, name):
        with open(name, "a+") as f:
            f.write(f"#----------/MD Parameter/----------# \n")

    @formatter(Parameter._chgParam)
    def _write_charge(self, name):
        with open(name, "a+") as f:
            f.write(f"#----------/Charge Parameter/----------# \n")

    @formatter(Parameter._dosParam)
    def _write_density(self, name):
        with open(name, "a+") as f:
            f.write(f"#----------/DOS Parameter/----------# \n")

    @formatter(Parameter._freqParam)
    def _write_freq(self, name):
        with open(name, "a+") as f:
            f.write(f"#----------/Frequency Parameter/----------# \n")

    @formatter(Parameter._stmParam)
    def _write_stm(self, name):
        with open(name, "a+") as f:
            f.write(f"#----------/STM Parameter/----------# \n")

    @formatter(Parameter._vtstParam)
    def _write_vtst(self, name):
        with open(name, "a+") as f:
            f.write(f"#----------/VTST optimizer Parameter/----------# \n")

    @formatter(Parameter._nebParam)
    def _write_neb(self, name):
        with open(name, "a+") as f:
            f.write(f"#----------/NEB Parameter/----------# \n")

    @formatter(Parameter._dimerParam)
    def _write_dimer(self, name):
        with open(name, "a+") as f:
            f.write(f"#----------/Dimer Parameter/----------# \n")

    @formatter(Parameter._plusUParam)
    def _write_plusU(self, name):
        with open(name, "a+") as f:
            f.write(f"#----------/+U Parameter/----------# \n")


class KPOINTS(MetaFile):
    def __init__(self, name, task='opt'):
        super(KPOINTS, self).__init__(name=name)
        self.task = task
        self.title, self.strategy, self.center, self.number, self.weight = None, None, None, None, None

        self._parse()

    def _parse(self):
        if self.task in ['opt']:
            self.title = self.strings[0].strip()
            self.strategy = self.strings[1].strip()
            self.center = self.strings[2].strip()
            self.number = list(map(int, self.strings[3].split()))
            self.weight = list(map(float, self.strings[4].split()))

    def write(self, name):
        with open(name) as f:
            f.write(self.title)
            f.write(self.strategy)
            f.write(self.center)
            f.write(self.number)
            f.write(self.weight)

    @staticmethod
    def min_number(lattice: Lattice, length=20.0):
        return np.ceil(length / lattice.length).astype(int)


class POTCAR(MetaFile):
    def __init__(self, name):
        super(POTCAR, self).__init__(name=name)
        self.potential, self.element = None, None

        if Path(self.name).exists():
            self._parse()

    def __add__(self, other):
        potential = self.potential if isinstance(self.potential, list) else [self.potential]
        element = self.element if isinstance(self.element, list) else [self.element]
        strings = self._strings

        potential += other.potential
        element += other.element
        strings += other._strings

        potcar = POTCAR("POTCAR")
        potcar.potential = potential
        potcar.element = element
        potcar._strings = strings
        return potcar

    def _parse(self):
        self.potential = [line.split()[2] for line in self.strings if line.find("TITEL") != -1]
        self.element = [line.split()[3] for line in self.strings if line.find("TITEL") != -1]

    @staticmethod
    def cat(potentials, elements: List[str], potdir=f"{RootDir}/pot"):

        if potdir is None or not Path(potdir).exists():
            raise PotDirNotExistError(f"potdir = {potdir} is not exist (should named as `pot`), please check")

        if (isinstance(potentials, str) and potentials not in POTENTIAL) or \
                (isinstance(potentials, list) and len(set(potentials).difference(set(POTENTIAL)))):
            raise TypeError(f"potentials should be {POTENTIAL}")

        if isinstance(potentials, str):
            potdir = Path(potdir) / potentials
            potcar = reduce(add, [POTCAR(name=(potdir / Path(element) / "POTCAR")) for element in elements])
        elif isinstance(potentials, list) and len(potentials) == len(elements):
            potcar = reduce(add, [POTCAR(name=Path(potdir) / potential / Path(element) / "POTCAR")
                                  for potential, element in zip(potentials, elements)])
        else:
            raise ParameterError(f"{potentials} and {elements} is not match")

        return potcar

    def write(self, name):
        with open(name, "w") as f:
            f.writelines(self.strings)


class XSDFile(MetaFile):
    def __init__(self, name):
        super(XSDFile, self).__init__(name=name)

        self._xml = None
        self.element, self.spin, self.frac_coord, self.selective_dynamics, self.lattice = None, None, None, None, None
        self._parse()

    @property
    def strings(self):
        if self._strings is None:
            with open(self.name, "r") as f:
                self._strings = f.read()
        return self._strings

    def _parse(self):
        self._xml = etree.XML(self.strings.encode("utf-8"))
        Atom3d = self._xml.xpath("//Atom3d[@Components]")
        Components = self._xml.xpath("//Atom3d//@Components")
        Name = [atom.attrib.get('Name', atom.attrib['Components']) for atom in Atom3d]
        FormalSpin = [int(atom.attrib.get('FormalSpin', '0')) for atom in Atom3d]
        XYZ = [list(map(float, item.split(","))) for item in self._xml.xpath("//Atom3d//@XYZ")]
        RestrictedProperties = [atom.attrib.get('RestrictedProperties', 'T T T') for atom in Atom3d]
        TF = [item.replace("FractionalXYZ", "F F F").split() for item in RestrictedProperties]
        assert len(XYZ) == len(Components) == len(Name) == len(FormalSpin) == len(
            TF), "Size of atom's information is not match"

        SpaceGroup = self._xml.xpath("//SpaceGroup")[0]
        Vector = [list(map(float, SpaceGroup.attrib[key].split(","))) for key in SpaceGroup.keys() if "Vector" in key]

        self.element = Components
        self.spin = FormalSpin
        self.frac_coord = XYZ
        self.selective_dynamics = TF
        self.lattice = Vector

    @property
    def structure(self):
        results = sorted(zip(range(len(self.element)), self.element, self.frac_coord), key=lambda x: (x[1], x[2][2]))
        sorted_order, sorted_element, sorted_frac_coord = list(zip(*results))
        sorted_selective_dynamics = np.array(self.selective_dynamics)[list(sorted_order)]
        atoms = Atoms(formula=sorted_element, frac_coord=sorted_frac_coord, selective_matrix=sorted_selective_dynamics)
        lattice = Lattice(np.array(self.lattice))
        return Structure(atoms=atoms, lattice=lattice)


class POSCAR(StructInfoFile):
    @staticmethod
    def dist(pos1: str, pos2: str):
        """
        Calculate the distance of two POSCAR, distance = sqrt(sum((i-j)**2))

        @param:
            pos1:   first POSCAR file name
            pos2:   second POSCAR file name
        """
        structure1 = POSCAR(name=pos1).structure
        structure2 = POSCAR(name=pos2).structure
        return Structure.dist(structure1, structure2)

    @staticmethod
    def align(pos1: str, pos2: str):
        """
        Tailor the atoms' order to make the distance of pos1 and pos2 minimum

        @param:
            pos1:   first POSCAR file name
            pos2:   second POSCAR file name
        """
        logger = Logger().logger

        structure1 = POSCAR(name=pos1).structure
        structure2 = POSCAR(name=pos2).structure
        logger.info(f"Align before: dist = {Structure.dist(structure1, structure2)}")
        structure1_new, structure2_new = Structure.align(structure1, structure2)
        logger.info(f"Align before: dist = {Structure.dist(structure1_new, structure2_new)}")
        structure1_new.write_POSCAR(f"{pos1}_sort")
        structure2_new.write_POSCAR(f"{pos2}_sort")
        logger.info(f"New structure have been written to *_sort files")


class CONTCAR(POSCAR):
    pass


class XDATCAR(StructInfoFile):
    def __init__(self, name):
        super().__init__(name)

        self.lattice = Lattice.from_string(self.strings[2:5])
        element_name = self.strings[5].split()
        element_count = [int(item) for item in self.strings[6].split()]
        self.element = sum([[name] * count for name, count in zip(element_name, element_count)], [])
        self.frames = [i for i in range(len(self.strings)) if self.strings[i].find("Direct") != -1]
        self._structure = []

    @property
    def structure(self):  # overwrite <structure method>
        if len(self._structure) == 0:
            for frame in self.frames:
                frac_coord = np.array([[float(item) for item in line.split()] for line in
                                       self.strings[frame + 1:frame + 1 + len(self.element)]])
                atoms = Atoms(formula=self.element, frac_coord=frac_coord)
                self._structure.append(Structure(atoms=atoms, lattice=self.lattice))
        return self._structure

    def movie(self, name):
        """Transform the XDATCAR to arc file"""
        ARCFile.write(name=name, structure=self.structure, lattice=self.lattice)


class DOSCAR(MetaFile):
    def __init__(self, name):
        super(DOSCAR, self).__init__(name=name)
        self.NAtom = int(self.strings[0].split()[0])
        self.Emax, self.Emin, self.NDOS, self.fermi = tuple(map(float, self.strings[5].split()[:4]))
        self.NDOS = int(self.NDOS)

    def load(self):
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

        return merge_dos(*dos_cython.load(self.strings, self.NDOS, self.fermi))


class EIGENVAL(MetaFile):
    def __init__(self, name):
        super(EIGENVAL, self).__init__(name=name)
        self.NKPoint, self.NBand = tuple(map(int, self.strings[5].split()[1:]))
        self.KPoint_coord = None
        self.energy = None

        self._parse()

    def _parse(self):
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
        logger = Logger().logger
        Path(directory).mkdir(exist_ok=True)
        for index in range(self.NBand):
            np.savetxt(f"{directory}/band_{index + 1}", self.energy[:, index])
        logger.info(f"Band data has been saved to {directory} directory")


class CHGBase(StructInfoFile):
    """
    Subclass of StructInfoFile, inherit <structure property>
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
        info = file_bind.load(self.name)
        self.NGX, self.NGY, self.NGZ = info.NGX, info.NGY, info.NGZ
        self.density = info.density
        assert self.density.size == self.NGX * self.NGY * self.NGZ, "Load density failure, size is not consistent"
        self.density = self.density.reshape((self.NGX, self.NGY, self.NGZ), order="F")
        return self

    def write(self, title=None, factor=1.0):
        """
        write CHGCAR_* file from array

        @param:
            system:     specify the structure system
            factor:     coordination factor
        """
        self.structure.write_POSCAR(name=self.__class__.__name__, title=title, factor=factor)
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
        transform CHGCAR_mag to grd file

        param:
            name:       specify the name of grd file
            DenCut:     density lower than DenCut will be set to zero (default: -1: disable the DenCut option)
        """
        file_bind.to_grd(name, DenCut)


class CHGCAR(StructInfoFile):
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

        with open("CHGCAR_tot", "w") as tot, open("CHGCAR_mag", "w") as mag:
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
        self._neb = [line for line in self.strings if line.find("NEB:") != -1]
        self.spin, self.bands, self.kpoints, self.fermi, self.steps = None, None, None, None, None
        self.energy, self.force = None, None
        self.last_energy, self.last_force = None, None
        self._parse_base()

        self.frequency = None
        if len(self._frequency):
            self._parse_freq()

        self.kpoint_info, self.band_info = None, None
        self._parse_band()

        self.tangent, self.last_tangent = 0., 0.
        if len(self._neb):
            self._parse_neb()

    def _parse_base(self):
        self.spin = [int(line.split()[2]) for line in self.strings if line.find("ISPIN") != -1][0]
        self.bands, self.kpoints = \
            [(int(line.split()[-1]), int(line.split()[3])) for line in self.strings if line.find("NBANDS") != -1][0]
        steps = [(index, int(line.split()[2].split("(")[0]), int(line.split()[3].split(")")[0]))
                 for index, line in enumerate(self.strings) if line.find("Iteration") != -1]
        self.steps = namedtuple("Steps", ("index", "ionic", "electronic"))(*list(map(tuple, zip(*steps))))
        self.fermi = [float(line.split()[2]) for line in self.strings if line.find("E-fermi") != -1][-1]
        self.energy = [float(line.split()[3]) for line in self.strings if line.find("energy  without") != -1]
        self.force = [float(line.split()[5]) for line in self.strings if line.find("FORCES: max atom") != -1]
        self.last_energy = self.energy[-1] if len(self.energy) else None
        self.last_force = self.force[-1] if len(self.force) else None

    def _parse_freq(self):
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

        self.frequency = namedtuple("Frequency", ("image", "wave_number", "coord", "vibration"))(image,
                                                                                                 np.array(wave_number),
                                                                                                 np.array(coord),
                                                                                                 np.array(vibration))

    def _parse_band(self):
        """
        Parse band information from OUTCAR

        @return:
            register self.kpoint_info (type: tuple(List[KPoint(coord, value)], List[KPoint(coord, value)]))
        """

        def spin_obtain(kpoint_group):
            """
            According to the index-list of kpoint in OUTCAR, parse the band_info

            @param:
                kpoint_group:       list, record the index of 'k-point' field occurrence in OUTCAR

            @return:
                spin:      List[KPoint(coord, value)], record the each k-point info
            """

            spin = []
            trans_func = lambda x: [int(x[0]), float(x[1]) - self.fermi, float(x[2])]  # format transform
            # parse band_info
            for index in kpoint_group:
                coord = list(map(float, band_info[index].split()[3:]))
                value = list(map(trans_func, np.char.split(band_info[index + 2:index + 2 + self.bands])))
                spin.append(KPoint(coord, np.array(value)))

            return spin

        def transform_band(spin):
            band = []
            for kpoint in spin:
                band.append(kpoint.value[:, 1])

            band = np.array(band)
            band = band.transpose((1, 0))
            return band

        content = self.strings[self.steps.index[-1]:]  # calculate bandgap from last step
        start_index = [index for index, line in enumerate(content) if line.find("E-fermi") != -1][0]
        end_index = [index for index, line in enumerate(content) if line.find("-----") != -1 and index > start_index][0]
        band_info = content[start_index:end_index]  # band_info content in last step
        KPoint = namedtuple("KPoint", ("coord", "value"))  # including `kpoint coord` and `each band energy`
        if self.spin == 2:
            kpoint_index = [index for index, line in enumerate(band_info) if line.find("k-point") != -1]
            half_len = int(len(kpoint_index) / 2)
            kpoint_up, kpoint_down = kpoint_index[:half_len], kpoint_index[half_len:]  # 'k-point' occurrence index

            spin_up = spin_obtain(kpoint_up)
            spin_down = spin_obtain(kpoint_down)

            self.kpoint_info = namedtuple("KPoint_info", ("up", "down"))(spin_up, spin_down)
            self.band_info = namedtuple("Band_info", ("up", "down"))(transform_band(spin_up), transform_band(spin_down))
        else:
            raise NotImplementedError("Non-spin polarized calculation has not been implemented")

    def _parse_neb(self):
        self.tangent = [float(line.split()[-1]) for line in self.strings if line.find("tangent") != -1]
        self.last_tangent = self.tangent[-1]

    def bandgap(self, cutoff=0.01):
        """
        Calculated the bandgap from OUTCAR file

        @param:
            cutoff:     any occupy lower than cutoff will be treated as the empty state

        @return:
            type:       type of bandgap, ['direct', 'indirect']
            bandgap:    value of bandgap
        """

        def MO_obtain(spin):
            """
            According to the kpoint_info, return the homo and lumo

            @param:
                spin:       List[KPoint(coord, value)], record the each k-point info

            @return:
                homo_spin:      KPoint(coord, value), record the homo information
                lumo_spin:      KPoint(coord, value), record the lumo information
            """

            # calculate homo and lumo
            homo_spin, lumo_spin = None, None
            for item in spin:
                lumo_index = np.where(item.value[:, 2] <= cutoff)[0][0]
                homo_index = lumo_index - 1
                homo, lumo = item.value[homo_index], item.value[lumo_index]
                homo_spin = KPoint(item.coord, homo) if homo_spin is None or homo_spin.value[1] < homo[1] else homo_spin
                lumo_spin = KPoint(item.coord, lumo) if lumo_spin is None or lumo_spin.value[1] > lumo[1] else lumo_spin
            return homo_spin, lumo_spin

        KPoint = namedtuple("KPoint", ("coord", "value"))  # including `kpoint coord` and `each band energy`
        if self.spin == 2:

            homo_up, lumo_up = MO_obtain(self.kpoint_info[0])
            homo_down, lumo_down = MO_obtain(self.kpoint_info[1])

            homo_real = homo_up if homo_up.value[1] > homo_down.value[1] else homo_down
            lumo_real = lumo_up if lumo_up.value[1] < lumo_down.value[1] else lumo_down

            if homo_real.coord == lumo_real.coord:
                return "direct", lumo_real.value[1] - homo_real.value[1]
            else:
                return "indirect", lumo_real.value[1] - homo_real.value[1]
        else:
            raise NotImplementedError("Non-spin polarized calculation has not been implemented")

    def animation_freq(self, freq: [str, int] = "image", frames: int = 30, scale: float = 0.6):
        """
        Generate freq.arc file from OUTCAR

        @param:
            freq:       specify which freq you want to animate, accept [int, str] arguments
            frames:     specify how many points you want to interpolate along one direction, default = 30
            scale:      determine the vibration scale, default = 0.6
        """
        logger = Logger().logger

        if self.frequency is None:
            raise AnimationError(f"{self.name} don't include frequency information")

        if isinstance(freq, int) and freq not in range(len(self._frequency)):
            raise FrequencyError(f"freq{freq} is not in {self.name}, should be {list(range(len(self._frequency)))}")

        if isinstance(freq, str) and freq != "image":
            raise FrequencyError(f"`{freq}` is not supported, should be `image`")

        freq = [index for index, item in enumerate(self.frequency.image) if item] if isinstance(freq, str) else freq

        if len(freq) == 0:
            raise FrequencyError(f"`{freq}` frequency is not found")

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
            logger.info(f"Processing freq{freq_index + 1} file ...")
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

        logger.info(f"All freq transform to corresponding *.arc files")


class MODECAR(MetaFile):
    @staticmethod
    def write_from_freq(freq: int, scale: float, outcar="OUTCAR"):
        """
        Generate MODECAR file from the `image-freq`

        @param:
            freq:       which freq you want to generate MODECAR
            scale:      scale factor, may lower than 1.0
            outcar:     name of the OUTCAR
        """
        outcar = OUTCAR(name=outcar)
        frequency = outcar.frequency.vibration[freq]
        np.savetxt("MODECAR", frequency * scale, fmt="%10.5f")

    @staticmethod
    def write_from_POSCAR(pos1: str, pos2: str):
        """
        Generate MODECAR file from the two `POSCAR` file

        @param:
            pos1:      name of first POSCAR file
            pos2:      name of second POSCAR file
        """
        structure1 = POSCAR(pos1).structure
        structure2 = POSCAR(pos2).structure
        assert structure1 == structure2, f"{pos1} and {pos2} are not structure match"
        diff = structure1 - structure2
        dist = Structure.dist(structure1, structure2)
        diff_norm = diff / dist
        np.savetxt("MODECAR", diff_norm, fmt="%20.10E")

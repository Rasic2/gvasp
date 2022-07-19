import math

from CLib import _dos
from pandas import DataFrame
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
    def to_structure(self):
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


if __name__ == '__main__':
    # # cc = VASPFile(name='test')
    # test = CONTCAR(name='CONTCAR-test')
    # structure = test.to_structure()
    # element = [' '] + structure.atoms.formula
    test = DOSCAR("DOSCAR-test")
    result = test.load()
    print()

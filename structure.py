import itertools

import numpy as np

from base import Atoms, Lattice
from logger import logger


class Structure(object):

    def __init__(self, atoms: Atoms = None, lattice: Lattice = None):
        """
        @parameter:
            atoms:              atoms of the structure, <class Atoms>
            lattice:            Lattice vector
            selective_matrix:   whether, or not move atoms in optimization

        @property:
            neighbour_tabel:    neighbour table of structure, number of neighbour_atom default is 12

        @func:
            find_neighbour_tables(self, neighbour_num: int = 12, adj_matrix=None) --> self.neighbour_table
            to_POSCAR(self, fname, system=None, factor=1): output the structure into `POSCAR/CONTCAR` file

            from_POSCAR(fname, style=None, mol_index=None, **kargs) --> Structure
            from_adj_matrix(structure, adj_matrix, adj_matrix_tuple, bond_dist3d, known_first_order) --> Structure
        """

        self.atoms = atoms
        self.lattice = lattice
        # self.neighbour_table = NeighbourTable(list)

    # def __sub__(self, other):
    #     diff_frac = self.atoms.frac_coord - other.atoms.frac_coord
    #     diff_frac = np.where(diff_frac>=0.5, diff_frac-1, diff_frac)
    #     diff_frac = np.where(diff_frac<=-0.5, diff_frac+1, diff_frac)
    #     diff_cart = np.dot(diff_frac, self.lattice.matrix)
    #     return diff_cart

    def __eq__(self, other):
        return self.lattice == other.lattice and self.atoms == other.atoms

    # def __repr__(self):
    #     return f"------------------------------------------------------------\n" \
    #            f"<Structure>                                                 \n" \
    #            f"-Lattice-                                                   \n" \
    #            f"{self.lattice.matrix}                                       \n" \
    #            f"-Atoms-                                                     \n" \
    #            f"{self.atoms}                                                \n" \
    #            f"------------------------------------------------------------" \
    #         if self.lattice is not None else f"<Structure object>"

    # def find_neighbour_table(self, neighbour_num: int = 12, adj_matrix=None):
    #     new_atoms = []
    #     neighbour_table = NeighbourTable(list)
    #     for atom_i in self.atoms:
    #         neighbour_table_i = []
    #         atom_j_list = self.atoms if adj_matrix is None else [self.atoms[atom_j_order] for atom_j_order in
    #                                                              adj_matrix[atom_i.order]]
    #         for atom_j in atom_j_list:
    #             if atom_i != atom_j:
    #                 image = Atom.search_image(atom_i, atom_j)
    #                 atom_j_image = Atom(formula=atom_j.formula, frac_coord=atom_j.frac_coord + image).set_coord(
    #                     lattice=self.lattice)
    #                 distance = np.linalg.norm(atom_j_image.cart_coord - atom_i.cart_coord)
    #                 logger.debug(f"distance={distance}")
    #                 if f'Element {atom_j.formula}' in atom_i.bonds.keys() and distance <= atom_i.bonds[
    #                     f'Element {atom_j.formula}'] * 1.1:
    #                     neighbour_table_i.append((atom_j, distance, (atom_j_image.cart_coord - atom_i.cart_coord), 1))
    #                 else:
    #                     neighbour_table_i.append((atom_j, distance, (atom_j_image.cart_coord - atom_i.cart_coord), 0))
    #         neighbour_table_i = sorted(neighbour_table_i,
    #                                    key=lambda x: x[1]) if adj_matrix is None else neighbour_table_i
    #         neighbour_table[atom_i] = neighbour_table_i[:neighbour_num]
    #
    #         # update coordination number
    #         atom_i.coordination_number = sum([item[3] for item in neighbour_table_i])
    #         new_atoms.append(atom_i)
    #     self.atoms = Atoms.from_list(new_atoms)
    #
    #     if adj_matrix is None:
    #         sorted_neighbour_table = NeighbourTable(list)
    #         for key, value in neighbour_table.items():
    #             sorted_neighbour_table[key] = sorted(value, key=lambda x: x[1])
    #         setattr(self, "neighbour_table", sorted_neighbour_table)
    #     else:
    #         setattr(self, "neighbour_table", neighbour_table)

    @staticmethod
    def from_POSCAR(name):
        logger.debug(f"Handle the {name}")
        with open(name) as f:
            cfg = f.readlines()
        lattice = Lattice.from_string(cfg[2:5])

        formula = [(name, int(count)) for name, count in zip(cfg[5].split(), cfg[6].split())]
        formula = sum([[formula] * count for (formula, count) in formula], [])

        selective = cfg[7].lower()[0] == "s"
        coor_type_index = 8 if selective else 7

        coor_type = cfg[coor_type_index].rstrip()
        coords = np.array(
            [[float(item) for item in coor.split()[:3]] for coor in
             cfg[coor_type_index + 1:coor_type_index + 1 + len(formula)]])

        frac_coord = coords if coor_type.lower()[0] == "d" else None
        cart_coord = coords if coor_type.lower()[0] == "c" else None
        selective_matrix = np.array(
            list([item.split()[3:6] for item in
                  cfg[coor_type_index + 1:coor_type_index + 1 + len(formula)]])) if selective else None

        atoms = Atoms(formula=formula, frac_coord=frac_coord, cart_coord=cart_coord, selective_matrix=selective_matrix)
        atoms.set_coord(lattice)

        return Structure(atoms=atoms, lattice=lattice)

    #
    # @staticmethod
    # def from_adj_matrix(structure, adj_matrix, adj_matrix_tuple, bond_dist3d, known_first_order):
    #     """
    #     Construct a new structure from old structure's adj_matrix
    #
    #     @parameter
    #         adj_matrix:         shape: (N, M)
    #         adj_matrix_tuple:   shape: (N, M, 2)
    #         bond_dist3d:        shape: (N, M, 3)
    #     """
    #
    #     adj_matrix_tuple_flatten = adj_matrix_tuple.reshape(-1, 2)
    #     bond_dist3d_flatten = bond_dist3d.reshape(-1, 3)
    #
    #     # construct the search-map
    #     known_order = []  # search-map, shape: (N-1, 2)
    #     known_index = [known_first_order]  # shape: (N,)
    #     known_index_matrix = []  # search-map corresponding to the index of adj_matrix_tuple
    #     for index, item in enumerate(adj_matrix_tuple_flatten):
    #         if item[0] not in known_index and item[1] in known_index:
    #             try:
    #                 real_index = item[1] * adj_matrix.shape[1] + np.where(adj_matrix[item[1]] == item[0])[0][
    #                     0]  # fix bug: [4]: [1, 2, 8]; [8]: [1, 2, 5]
    #             except IndexError:
    #                 continue
    #             known_index.append(item[0])
    #             known_order.append((item[1], item[0]))
    #             known_index_matrix.append(real_index)
    #         if item[1] not in known_index and item[0] in known_index:
    #             known_index.append(item[1])
    #             known_order.append((item[0], item[1]))
    #             known_index_matrix.append(index)
    #         if len(known_index) == adj_matrix.shape[0]:
    #             break
    #
    #     # calculate the coord from the search-map
    #     known_first_atom = structure.atoms[known_first_order]
    #     known_dist3d = bond_dist3d_flatten[known_index_matrix]  # diff matrix, shape: (N-1, 3)
    #     known_atoms = [known_first_atom]
    #     for item, diff_coord in zip(known_order, known_dist3d):
    #         atom_new = copy.deepcopy(structure.atoms[item[1]])  # unknown atom
    #         atom_new.frac_coord = None
    #         for atom_known in known_atoms:
    #             if atom_known.order == item[0]:
    #                 atom_new.cart_coord = atom_known.cart_coord + diff_coord
    #                 known_atoms.append(atom_new)
    #     assert len(known_atoms) == adj_matrix.shape[0], "Search-map construct failure, please check the code!"
    #
    #     sorted_atoms = sorted(known_atoms, key=lambda atom: atom.order)
    #     sorted_atoms = [atom.set_coord(structure.lattice) for atom in sorted_atoms]
    #     atoms = Atoms.from_list(sorted_atoms)
    #
    #     return Structure(atoms=atoms, lattice=structure.lattice)

    def write(self, name, system=None, factor=1.0):
        system = system if system is not None else " ".join(
            [f"{key} {value}" for key, value in self.atoms.size.items()])
        lattice = self.lattice.strings
        elements = [(key, str(len(list(value)))) for key, value in itertools.groupby(self.atoms.formula)]
        element_name, element_count = list(map(list, zip(*elements)))
        element_name, element_count = " ".join(element_name), " ".join(element_count)
        selective = None not in getattr(self.atoms, "selective_matrix")
        coords = "\n".join([" ".join([f"{item:15.12f}" for item in atom.frac_coord]) for atom in self.atoms])
        if selective:
            coords = "".join([coord + "\t" + "   ".join(selective_matrix) + "\n" for coord, selective_matrix in
                              zip(coords.split("\n"), self.atoms.selective_matrix)])

        with open(name, "w") as f:
            f.write(f"{system}\n")
            f.write(f"{factor}\n")
            f.write(lattice)
            f.write(f"{element_name}\n")
            f.write(f"{element_count}\n")
            if selective:
                f.write("Selective Dynamics\n")
            f.write("Direct\n")
            f.write(coords)
            f.write("\n\n")

        logger.debug(f"{name} write finished!")

# class NeighbourTable(defaultdict):
#
#     def __repr__(self):
#         return " ".join([f"{key} <---> <{value[0]}> \n" for key, value in self.items()])
#
#     @property
#     def index(self):  # adj_matrix
#         return np.array([[value[0].order for value in values] for key, values in self.items()])
#
#     @property
#     def index_tuple(self):  # adj_matrix_tuple
#         return np.array([[(key.order, value[0].order) for value in values] for key, values in self.items()])
#
#     @property
#     def dist(self):
#         return np.array([[value[1] for value in values] for _, values in self.items()])
#
#     @property
#     def dist3d(self):
#         return np.array([[value[2] for value in values] for _, values in self.items()])
#
#     @property
#     def coordination(self):
#         return np.array([sum([value[3] for value in values]) for _, values in self.items()])

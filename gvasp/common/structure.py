import copy
import itertools
import logging
import os
from collections import defaultdict, Counter

import numpy as np

from gvasp.common.base import Atoms, Lattice, Atom
from gvasp.common.error import StructureOverlapError

logger = logging.getLogger(__name__)


class Structure(object):

    def __init__(self, atoms: Atoms = None, lattice: Lattice = None):
        """
        @parameter:
            atoms:              atoms of the structure, <class Atoms>
            lattice:            Lattice vector

        @property:
            neighbour_tabel:    neighbour table of structure, number of neighbour_atom default is 12

        @func:
            find_neighbour_tables(self, neighbour_num: int = 12, adj_matrix=None) --> self.neighbour_table

            dist(structure1, structure2): calculate distance between two structures
            align(structure1, structure2, tolerance1=0.2, tolerance2=100): tailor atoms' order to align structures
            from_file(name, style=None, mol_index=None, **kargs) --> Structure

            write(self, name, system=None, factor=1): output the structure into `POSCAR/CONTCAR` file
        """

        self.atoms = atoms
        self.lattice = lattice
        self.neighbour_table = NeighbourTable(list)

    def __sub__(self, other):
        diff_frac = self.atoms.frac_coord - other.atoms.frac_coord
        diff_frac = np.where(diff_frac >= 0.5, diff_frac - 1, diff_frac)
        diff_frac = np.where(diff_frac <= -0.5, diff_frac + 1, diff_frac)
        diff_cart = np.dot(diff_frac, self.lattice.matrix)
        return diff_cart

    def __eq__(self, other):
        return self.lattice == other.lattice and self.atoms == other.atoms

    def __repr__(self):
        return f'------------------------------------------------------------\n' \
               f'<Structure>                                                 \n' \
               f'-Lattice-                                                   \n' \
               f'{self.lattice.matrix}                                       \n' \
               f'-Atoms-                                                     \n' \
               f'{self.atoms}                                                \n' \
               f'------------------------------------------------------------' \
            if self.lattice is not None else f'<Structure object>'

    @staticmethod
    def dist(structure1, structure2):
        """
        Calculate the distance of two structures, distance = sqrt(sum((i-j)**2))

        @param:
            structure1:   first Structure
            structure2:   second Structure

        @return
            diff:   distance between two structures
        """
        diff = structure1 - structure2
        diff = np.sum(diff ** 2) ** 0.5
        return diff

    @staticmethod
    def align(structure1, structure2, tolerance1=0.2, tolerance2=100):
        """
        Tailor the atoms' order to make the distance of structure1 and structure2 minimum

        @param:
            structure1:     first Structure
            structure2:     second Structure
            tolerance1:     first sort tolerance
            tolerance2:     second sort tolerance
        """

        def sort(atoms1, match_list, atoms1_sort, atoms2_sort, tolerance=0.2):
            for atom_i in atoms1:
                distances_candidate = []
                bonds_i = Counter([item[0].formula for item in atom_i.bonds])
                for atom_j in match_list:
                    bonds_j = Counter([item[0].formula for item in atom_j.bonds])
                    formula_cond = (atom_j.formula == atom_i.formula)
                    bonds_cond = (bonds_i == bonds_j)
                    if formula_cond and (bonds_cond or tolerance >= 10):
                        image = Atom.search_image(atom_i, atom_j)
                        atom_j_image = Atom(formula=atom_j.formula, frac_coord=atom_j.frac_coord + image).set_coord(
                            lattice=structure2.lattice)
                        distance = np.linalg.norm(atom_j_image.cart_coord - atom_i.cart_coord)
                        logger.debug(f'distance={distance}')
                        if distance <= tolerance:
                            distances_candidate.append((atom_j, distance))
                if len(distances_candidate):
                    sorted_distances_candidate = sorted(distances_candidate, key=lambda x: x[1])
                    atoms1_sort.append(atom_i)
                    atoms2_sort.append(sorted_distances_candidate[0][0])
                    match_list.remove(sorted_distances_candidate[0][0])
            return atoms1_sort, atoms2_sort

        if not len(structure1.atoms.bonds):
            structure1.find_neighbour_table()

        if not len(structure2.atoms.bonds):
            structure2.find_neighbour_table()

        atoms1, atoms2 = structure1.atoms, structure2.atoms

        match_list = copy.deepcopy(atoms2.atom_list)
        atoms1_sort, atoms2_sort = [], []

        # First align, according to the `min_distance rule`
        atoms1_sort, atoms2_sort = sort(atoms1, match_list, atoms1_sort, atoms2_sort, tolerance1)

        # Second align
        atoms1_remain = [atom for atom in atoms1 if atom not in atoms1_sort]
        atoms2_remain = [atom for atom in atoms2 if atom not in atoms2_sort]
        atoms1_sort, atoms2_sort = sort(atoms1_remain, atoms2_remain, atoms1_sort, atoms2_sort, tolerance2)

        # construct new structure
        for atom_i, atom_j in zip(atoms1_sort, atoms2_sort):
            atom_i.order, atom_j.order = None, None
        atoms1_new, atoms2_new = Atoms.from_list(atoms1_sort), Atoms.from_list(atoms2_sort)
        structure1_new = Structure(atoms=atoms1_new, lattice=structure1.lattice)
        structure2_new = Structure(atoms=atoms2_new, lattice=structure2.lattice)
        return structure1_new, structure2_new

        # TODO: performance optimization

    def find_neighbour_table(self, neighbour_num: int = 12, cut_radius=None, adj_matrix=None, sort=True,
                             including_self=False):
        new_atoms = []
        neighbour_table = NeighbourTable(list)
        for atom_i in self.atoms:
            neighbour_table_i = []
            atom_j_list = self.atoms if adj_matrix is None else [self.atoms[atom_j_order] for atom_j_order in
                                                                 adj_matrix[atom_i.order]]
            for atom_j in atom_j_list:
                if not including_self and atom_i == atom_j:
                    continue
                image = Atom.search_image(atom_i, atom_j)
                atom_j_image = Atom(formula=atom_j.formula, frac_coord=atom_j.frac_coord + image).set_coord(
                    lattice=self.lattice)
                distance = np.linalg.norm(atom_j_image.cart_coord - atom_i.cart_coord)
                logger.debug(f'distance={distance}')
                if f'Element {atom_j.formula}' in atom_i._default_bonds.keys() \
                        and distance <= atom_i._default_bonds[f'Element {atom_j.formula}'] * 1.1:
                    neighbour_table_i.append((atom_j, distance, (atom_j_image.cart_coord - atom_i.cart_coord), 1))
                else:
                    neighbour_table_i.append((atom_j, distance, (atom_j_image.cart_coord - atom_i.cart_coord), 0))

            neighbour_table_i = sorted(neighbour_table_i,
                                       key=lambda x: x[1]) if adj_matrix is None and sort else neighbour_table_i
            if neighbour_num is not None:
                neighbour_table[atom_i] = neighbour_table_i[:neighbour_num]
            else:
                neighbour_table[atom_i] = neighbour_table_i

            if cut_radius is not None:
                neighbour_table[atom_i] = [item for item in neighbour_table[atom_i] if item[1] <= cut_radius]

            # update bonds && coordination number
            atom_i.bonds = [(item[0], item[1]) for item in neighbour_table_i if item[3]]
            atom_i.coordination_number = sum([item[3] for item in neighbour_table_i])
            new_atoms.append(atom_i)

        self.atoms = Atoms.from_list(new_atoms)
        setattr(self, 'neighbour_table', neighbour_table)

        return self

    def check_overlap(self, cutoff=0.1):
        self.find_neighbour_table(neighbour_num=1)
        dist = self.neighbour_table.dist.reshape(-1)
        if dist[np.where(dist <= cutoff)].size:
            raise StructureOverlapError(f"Exist atoms' distance <= {cutoff}, please check")
        else:
            logger.info('No structure overlap occurrence')

    @staticmethod
    def from_POSCAR(name):
        logger.debug(f'Handle the {name}')
        with open(name) as f:
            cfg = f.readlines()
        lattice = Lattice.from_string(cfg[2:5])

        formula = [(name, int(count)) for name, count in zip(cfg[5].split(), cfg[6].split())]
        formula = sum([[formula] * count for (formula, count) in formula], [])

        selective = cfg[7].lower()[0] == 's'
        coor_type_index = 8 if selective else 7

        coor_type = cfg[coor_type_index].rstrip()
        coords = np.array(
            [[float(item) for item in coor.split()[:3]] for coor in
             cfg[coor_type_index + 1:coor_type_index + 1 + len(formula)]])

        frac_coord = coords if coor_type.lower()[0] == 'd' else None
        cart_coord = coords if coor_type.lower()[0] == 'c' else None
        selective_matrix = np.array(
            list([item.split()[3:6] for item in
                  cfg[coor_type_index + 1:coor_type_index + 1 + len(formula)]])) if selective else None

        atoms = Atoms(formula=formula, frac_coord=frac_coord, cart_coord=cart_coord, selective_matrix=selective_matrix)
        atoms.set_coord(lattice)

        return Structure(atoms=atoms, lattice=lattice)

    @staticmethod
    def from_cell(name):
        logger.debug(f'Handle the {name}')
        with open(name, 'r') as f:
            strings = f.readlines()

        lattice_index = [index for index, line in enumerate(strings) if line.find('LATTICE_CART') != -1]
        atom_index = [index for index, line in enumerate(strings) if line.find('POSITIONS_FRAC') != -1]
        lattice = Lattice.from_string(strings[lattice_index[0] + 1:lattice_index[1]])
        atom = [(line.split()[0], line.split()[1:]) for line in strings[atom_index[0] + 1:atom_index[1]]]
        formula, frac_coord = list(map(list, zip(*atom)))
        frac_coord = list(map(lambda x: [float(x[0]), float(x[1]), float(x[2])], frac_coord))
        atoms = Atoms(formula=formula, frac_coord=frac_coord)

        return Structure(atoms=atoms, lattice=lattice)

    @staticmethod
    def from_structure(structure, coord, type='cart'):
        """
        Generate the Structure instance from original structure with changing its atoms' coord

        Args:
            structure: which structure you want to base
            coord: coord for new structure, <frac or cart>
            type: which type of new coord, should be one of ["frac", "cart"], default: "cart"

        Returns: new Structure instance

        """
        atoms = copy.deepcopy(structure.atoms)
        if type == 'cart':
            atoms.frac_coord = [None] * len(atoms)
            atoms.cart_coord = coord
        elif type == 'frac':
            atoms.cart_coord = [None] * len(atoms)
            atoms.frac_coord = coord
        else:
            raise TypeError(f'{type} not supported, should be `cart` or `frac`')
        atoms.set_coord(structure.lattice)
        return Structure(atoms=atoms, lattice=structure.lattice)

    def write_POSCAR(self, name, title=None, factor=1.0):
        title = title if title is not None else 'AutoGenerated'
        lattice = self.lattice.strings
        elements = [(key, str(len(list(value)))) for key, value in itertools.groupby(self.atoms.formula)]
        element_name, element_count = list(map(list, zip(*elements)))
        element_name, element_count = ' '.join(element_name), ' '.join(element_count)
        selective = None not in getattr(self.atoms, 'selective_matrix')
        coords = '\n'.join([' '.join([f'{item:15.12f}' for item in atom.frac_coord]) for atom in self.atoms])
        if selective:
            coords = ''.join([coord + '\t' + '   '.join(selective_matrix) + '\n' for coord, selective_matrix in
                              zip(coords.split('\n'), self.atoms.selective_matrix)])

        with open(name, 'w') as f:
            f.write(f'{title}\n')
            f.write(f'{factor}\n')
            f.write(lattice)
            f.write(f'{element_name}\n')
            f.write(f'{element_count}\n')
            if selective:
                f.write('Selective Dynamics\n')
            f.write('Direct\n')
            f.write(coords)
            f.write('\n\n')

        logger.debug(f'{name} write finished!')


class NeighbourTable(defaultdict):

    def __repr__(self):
        return ' '.join([f'{key} <---> <{value[0]}> \n' for key, value in self.items()])

    @property
    def index(self):  # adj_matrix
        return np.array([[value[0].order for value in values] for key, values in self.items()])

    @property
    def index_tuple(self):  # adj_matrix_tuple
        return np.array([[(key.order, value[0].order) for value in values] for key, values in self.items()])

    @property
    def dist(self):
        return np.array([[value[1] for value in values] for _, values in self.items()])

    @property
    def dist3d(self):
        return np.array([[value[2] for value in values] for _, values in self.items()])

    @property
    def coordination(self):
        return np.array([sum([value[3] for value in values]) for _, values in self.items()])

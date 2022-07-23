from collections import Counter
from pathlib import Path
from typing import List, Any

import numpy as np
import yaml

from logger import root_dir, logger

yaml.warnings({'YAMLLoadWarning': False})


class Lattice(object):

    def __init__(self, matrix: np.ndarray):
        self.matrix = matrix

    def __eq__(self, other):
        return np.all(self.matrix == other.matrix)

    def __hash__(self):
        return hash(self.volume)

    def __repr__(self):
        return f"{self.matrix}"

    @property
    def length(self):
        return np.power(np.sum(np.power(self.matrix, 2), axis=1), 0.5)

    @property
    def angle(self):
        alpha = np.arccos(np.dot(self.matrix[1], self.matrix[2]) / (self.length[1] * self.length[2])) * 180 / np.pi
        beta = np.arccos(np.dot(self.matrix[0], self.matrix[2]) / (self.length[0] * self.length[2])) * 180 / np.pi
        gamma = np.arccos(np.dot(self.matrix[0], self.matrix[1]) / (self.length[0] * self.length[1])) * 180 / np.pi
        return np.array([alpha, beta, gamma])

    @property
    def volume(self):
        return np.linalg.det(self.matrix)

    @property
    def inverse(self):
        return np.linalg.inv(self.matrix)

    @staticmethod
    def from_string(string):
        """
        @parameter
            string:     three-line <string>,
                        e.g.,    7.707464  0.000000  0.000000
                                -3.853732  6.674860  0.000000
                                 0.000000  0.000000 28.319031
        """
        matrix = np.array([[float(ii) for ii in item.split()[:3]] for item in string])
        return Lattice(matrix)

    @staticmethod
    def from_POSCAR(name):
        with open(name) as f:
            cfg = f.readlines()
        return Lattice.from_string(cfg[2:5])

    @property
    def strings(self):
        return "".join([" ".join([f"{ii:>9.6f}" for ii in item]) + "\n" for item in self.matrix])


class Atom(object):
    """
        `Atom class represent one atom in periodic solid system`

        @property
            formula:        chemical formula
            number:         atomic number
            period:         atomic period in element period table
            group:          atomic group in element period table
            color:          atomic color using RGB
            order:          atomic order in <Structure class>, default: 0
            frac_coord:     fractional coordinates  
            cart_coord:     cartesian coordinates
            bonds:          atomic default bond property {atom: bond-length}
        
        @func
            __initialize_attrs:     initialize the attributes from the element.yaml
    """
    _config_file = Path(f"{root_dir}/element.yaml")
    _attributes_yaml = ['number', 'period', 'group', 'color', 'bonds']
    _load = False
    _attrs = None

    def __new__(cls, *args, **kwargs):
        cls.__load_config()
        return super(Atom, cls).__new__(cls)

    def __init__(self, formula, order: (int, list) = 0, frac_coord=None, cart_coord=None, selective_matrix=None):
        self.formula = formula
        self.order = order
        self.frac_coord = np.array(frac_coord) if frac_coord is not None else None
        self.cart_coord = np.array(cart_coord) if cart_coord is not None else None
        self.selective_matrix = np.array(selective_matrix) if selective_matrix is not None else None

        # config atom from `element.yaml`
        self.number, self.period, self.group, self.color, self.bonds = (None, None, None, None, [])
        self.__initialize_attrs()

        # atom_type property
        self.coordination_number = None

    def __eq__(self, other):
        return self.number == other.number and self.order == other.order

    def __lt__(self, other):
        return self.number < other.number or self.order < other.order

    def __ge__(self, other):
        return self.number >= other.number or self.order >= other.order

    def __hash__(self):
        return hash(self.number) + hash(str(self.order))

    def __repr__(self):
        return f"(Atom {self.order} : {self.formula} : {self.cart_coord})"

    @classmethod
    def __load_config(cls):  # private classmethod
        if not cls._load:
            with open(cls._config_file) as f:
                cfg = f.read()
            cls._attrs = yaml.safe_load(cfg)
            cls._load = True

    def __initialize_attrs(self):  # private method
        if isinstance(self.formula, str):  # <class Atom>
            for key, value in self._attrs[f'Element {self.formula}'].items():
                setattr(self, key, value)
        elif isinstance(self.formula, list):  # <class Atoms>
            for attr in self._attributes_yaml:
                setattr(self, attr, [self._attrs[f'Element {formula}'][attr] for formula in self.formula])

    @property
    def atom_type(self):
        return f"{self.formula}{self.coordination_number}c"

    def set_coord(self, lattice: Lattice):
        assert lattice is not None
        if self.cart_coord is not None and self.frac_coord is None:
            self.frac_coord = np.dot(self.cart_coord, lattice.inverse)
        elif self.frac_coord is not None and self.cart_coord is None:
            self.cart_coord = np.dot(self.frac_coord, lattice.matrix)

        return self

    @staticmethod
    def search_image(atom_i, atom_j) -> np.ndarray:
        if not isinstance(atom_i, Atom) or not isinstance(atom_j, Atom):
            SystemError("The parameters should be <class Atom>!")
        logger.debug(
            f"Start search the {atom_i.formula}{atom_i.order}-{atom_j.formula}{atom_j.order} neighbour in all images!")
        image_pos = np.where(atom_j.frac_coord - atom_i.frac_coord <= 0.5, 0, -1)
        image_neg = np.where(atom_j.frac_coord - atom_i.frac_coord >= -0.5, 0, 1)
        image = image_pos + image_neg
        cod_frac = np.all(atom_j.frac_coord + image - atom_i.frac_coord <= 0.5) and np.all(
            atom_j.frac_coord + image - atom_i.frac_coord >= -0.5)
        if not cod_frac:
            SystemExit(f"Transform Error, exit!")
        logger.debug(f"Search the image {image} successfully!")

        return image


class Atoms(Atom):
    """
        `Atoms class represent atom set in periodic solid system`

        @property
            formula:        chemical formula, <list>
            number:         atomic number, <list>
            period:         atomic period in element period table, <list>
            group:          atomic group in element period table, <list>
            color:          atomic color using RGB, <list>
            order:          atomic order in <Structure class>, default: <list(range(len(formula)))>
            frac_coord:     fractional coordinates, <list>
            cart_coord:     cartesian coordinates, <list>
            bonds:          atomic default bond property {atom: bond-length}

            count:          total atom number in atom set
            size:           list atom number according to their formula

        @func
            __initialize_attrs:     initialize the attributes from the element.yaml
            from_list:              construct the <class Atoms> from an Atom list, i.e., [Atom, Atom, Atom] --> Atoms
    """

    def __new__(cls, *args, **kwargs):
        return super(Atoms, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        super(Atoms, self).__init__(*args, **kwargs)

        self.order = list(range(len(self.formula))) if isinstance(self.order, int) else self.order
        self.frac_coord = [None] * len(self.formula) if self.frac_coord is None else self.frac_coord
        self.cart_coord = [None] * len(self.formula) if self.cart_coord is None else self.cart_coord
        self.selective_matrix = [None] * len(self.formula) if self.selective_matrix is None else self.selective_matrix

        self.__index_list = []  # inner index-list

    def __len__(self) -> int:
        return len(self.formula)

    def __repr__(self):
        string = ""
        for order, formula, cart_coord in zip(self.order, self.formula, self.cart_coord):
            string += f"(Atom {order} : {formula} : {cart_coord}) \n"
        return string

    def __iter__(self):
        self.__index_list.append(0)
        return self

    def __next__(self):
        current_loop_index = self.__index_list[-1]  # record current-loop-index
        if current_loop_index < len(self):
            current_loop_index += 1
            self.__index_list[-1] = current_loop_index  # overwrite the original index
            return self[current_loop_index - 1]
        else:
            del (self.__index_list[-1])
            raise StopIteration

    def __contains__(self, atom):
        if atom in list(self):
            return True
        else:
            return False

    def __getitem__(self, index):
        atom = Atom(formula=self.formula[index], order=self.order[index],
                    frac_coord=self.frac_coord[index], cart_coord=self.cart_coord[index],
                    selective_matrix=self.selective_matrix[index])

        # update coordination number
        atom.coordination_number = self.coordination_number[index] if self.coordination_number is not None else None
        return atom

    @property
    def count(self) -> int:
        return len(self)

    @property
    def size(self):
        return Counter(self.formula)

    @property
    def atom_list(self):  # atom may update, so we don't use a static list
        return [atom for atom in self]

    @property
    def atom_type(self):  # override this property
        return [f"{atom.formula}{atom.coordination_number}c" for atom in self]

    def set_coord(self, lattice: Lattice):  # override this method
        assert lattice is not None
        if None not in self.cart_coord and None in self.frac_coord:
            self.frac_coord = np.dot(self.cart_coord, lattice.inverse)
        elif None not in self.frac_coord and None in self.cart_coord:
            self.cart_coord = np.dot(self.frac_coord, lattice.matrix)

        return self

    @staticmethod
    def from_list(atoms: list):
        formula = [atom.formula for atom in atoms]
        order: List[Any] = [atom.order for atom in atoms]
        frac_coord = [atom.frac_coord for atom in atoms]
        cart_coord = [atom.cart_coord for atom in atoms]
        selective_matrix = [atom.selective_matrix for atom in atoms]
        coordination_number = [atom.coordination_number for atom in atoms]

        # update coordination number
        new_atoms = Atoms(formula=formula, order=order, frac_coord=frac_coord,
                          cart_coord=cart_coord, selective_matrix=selective_matrix)
        new_atoms.coordination_number = coordination_number
        return new_atoms

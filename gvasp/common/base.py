import copy
from collections import Counter
from itertools import groupby
from math import cos, sin
from pathlib import Path
from typing import List, Any

import numpy as np
import yaml
from gvasp.lib.base_bind import search_image as search_image_bind

from gvasp.common.setting import RootDir
from gvasp.common.utils import redefine_frac

yaml.warnings({'YAMLLoadWarning': False})


class Lattice(object):

    def __init__(self, matrix: np.ndarray):
        """
        Initialize of Lattice class

        Args:
            matrix (np.ndarray): use a (3x3) np.ndarray matrix to initialize the Lattice
        """
        self.matrix = matrix

    def __eq__(self, other):
        return np.all(self.matrix == other.matrix)

    def __hash__(self):
        return hash(self.volume)

    def __repr__(self):
        return f"{self.matrix}"

    @property
    def strings(self) -> str:
        """
        Transform a Lattice instance to string

        Returns:
            strings (str): Lattice instance in string format
        """
        return "".join([" ".join([f"{ii:>9.6f}" for ii in item]) + "\n" for item in self.matrix])

    @property
    def length(self) -> np.ndarray:
        """
        Calculate the lattice length

        Returns:
            length (np.ndarray): store the length, shape = (3x1)
        """
        return np.power(np.sum(np.power(self.matrix, 2), axis=1), 0.5)

    @property
    def angle(self) -> np.ndarray:
        """
        Calculate the lattice angle

        Returns:
            angle (np.ndarray): store the angle, shape = (3x1)
        """
        alpha = np.arccos(np.dot(self.matrix[1], self.matrix[2]) / (self.length[1] * self.length[2])) * 180 / np.pi
        beta = np.arccos(np.dot(self.matrix[0], self.matrix[2]) / (self.length[0] * self.length[2])) * 180 / np.pi
        gamma = np.arccos(np.dot(self.matrix[0], self.matrix[1]) / (self.length[0] * self.length[1])) * 180 / np.pi
        return np.array([alpha, beta, gamma])

    @property
    def volume(self) -> float:
        """
        Calculate the lattice volume

        Returns:
            volume (float): store the volume
        """
        return np.linalg.det(self.matrix)

    @property
    def inverse(self) -> np.ndarray:
        """
        Calculate the inverse matrix of lattice

        Returns:
            inverse (np.ndarray): store the inverse matrix
        """
        return np.linalg.inv(self.matrix)

    @staticmethod
    def arc_lattice(lattice):
        """
        Construct a Arc Lattice instance from lattice

        Args:
            lattice (Lattice): Lattice instance

        Returns:
            arc lattice (Lattice): Lattice instance
        """
        la, lb, lc = lattice.length
        alpha, beta, gamma = lattice.angle / 180. * np.pi
        matrix = np.array([[la, 0., 0.],
                           [lb * cos(gamma), lb * sin(gamma), 0.],
                           [lc * cos(beta), lc * (cos(alpha) - cos(beta) * cos(gamma)) / sin(gamma),
                            lc * (1 + 2 * cos(gamma) * cos(beta) * cos(alpha) - cos(alpha) ** 2 - cos(beta) ** 2 - cos(
                                gamma) ** 2) ** 0.5 / sin(gamma)]
                           ])
        return Lattice(matrix)

    @staticmethod
    def from_string(string):
        """
        Construct a Lattice instance from string

        Args:
            string (List[str]): three-line <string>

                Examples
                ---------
                >>> string
                array([[  7.707464,  0.000000,  0.000000],
                         -3.853732,  6.674860,  0.000000],
                          0.000000,  0.000000, 28.319031]])

        Returns:
            lattice (Lattice): Lattice instance
        """
        matrix = np.array([[float(num) for num in re.findall(r'[+-]?\d+\.?\d*(?:[eE][+-]?\d+)?', line)[:3]] for line in string])
        return Lattice(matrix)

    @staticmethod
    def from_POSCAR(name):
        """
        Construct a Lattice instance from POSCAR file

        Args:
            name ([str, Path]): path of POSCAR

        Returns:
            lattice (Lattice): Lattice instance
        """
        with open(name) as f:
            cfg = f.readlines()
        return Lattice.from_string(cfg[2:5])


class  Atom(object):
    """
    Atom class represent one atom in periodic solid system

    Attributes:
        formula (str): chemical formula
        number (int): atomic number
        period (int): atomic period in element period table
        group (int): atomic group in element period table
        color (str): atomic color using RGB
        order (int): atomic order in <Structure class>, default: 0
        frac_coord (np.ndarray): fractional coordinates
        cart_coord (np.ndarray): cartesian coordinates
        _default_bonds: atomic default bond property {atom: bond-length}

    Methods:
        atom_type(self) -> property: register atom_type property
        set_coord(self, lattice: Lattice) -> object: recalculate frac_coord from cart_coord / recalculate cart_coord
                                                     from frac_coord
        search_image(atom_i, atom_j) -> np.ndarray: search the nearest image in which have minimum distance between
                                                    two atoms

        __load_config(cls): load element.yaml file
        __initialize_attrs(self): initialize the attributes from the element.yaml
    """

    _config_file = Path(f"{RootDir}/element.yaml")
    _attributes_yaml = ['number', '_default_bonds']
    _load = False
    _attrs = None

    def __new__(cls, *args, **kwargs):
        cls.__load_config()
        return object.__new__(cls)

    def __init__(self, formula, order: (int, list) = 0, frac_coord=None, cart_coord=None, selective_matrix=None,
                 constrain=False, spin=0):
        self.formula = formula
        self.order = order
        self.frac_coord = redefine_frac(np.array(frac_coord)) if frac_coord is not None else None
        self.cart_coord = np.array(cart_coord) if cart_coord is not None else None
        self.selective_matrix = np.array(selective_matrix) if selective_matrix is not None else None
        self.constrain = constrain
        self.spin = spin

        # config atom from `element.yaml`
        self.number, self._default_bonds = (None, [])
        self.__initialize_attrs()

        # atom_type property
        self.coordination_number = None

        # bonds information
        self.bonds = []

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
    def __load_config(cls):
        """load element.yaml file (private classmethod)"""
        if not cls._load:
            with open(cls._config_file) as f:
                cfg = f.read()
            cls._attrs = yaml.safe_load(cfg)
            cls._load = True

    def __initialize_attrs(self):
        """initialize the attributes from the element.yaml (private method)"""
        if isinstance(self.formula, str):  # <class Atom>
            for key, value in self._attrs[f'Element {self.formula}'].items():
                setattr(self, key, value)
        elif isinstance(self.formula, list):  # <class Atoms>
            for attr in self._attributes_yaml:
                setattr(self, attr, [self._attrs[f'Element {formula}'][attr] for formula in self.formula])

    @property
    def atom_type(self):
        """register atom_type property"""
        return f"{self.formula}{self.coordination_number}c"

    def set_coord(self, lattice: Lattice):
        """
        recalculate frac_coord from cart_coord / recalculate cart_coord from frac_coord

        Args:
            lattice (Lattice): Lattice instance
        """
        assert lattice is not None
        if self.cart_coord is not None and self.frac_coord is None:
            self.frac_coord = np.dot(self.cart_coord, lattice.inverse)
        elif self.frac_coord is not None and self.cart_coord is None:
            self.cart_coord = np.dot(self.frac_coord, lattice.matrix)

        return self

    @staticmethod
    def search_image(atom_i, atom_j) -> np.ndarray:
        """
        search the nearest image in which have minimum distance between two atoms

        Args:
            atom_i (Atom): Atom instance
            atom_j (Atom): Atom instance

        Returns:
            image (np.ndarray): record the transform direction
        """

        if not isinstance(atom_i, Atom) or not isinstance(atom_j, Atom):
            SystemError("The parameters should be <class Atom>!")

        return search_image_bind(atom_i.frac_coord, atom_j.frac_coord)

    @staticmethod
    def distance(atom_i, atom_j, lattice: Lattice):
        if not isinstance(atom_i, Atom) or not isinstance(atom_j, Atom):
            raise TypeError(f"{atom_i} and {atom_j} should be <class Atom>")

        image = Atom.search_image(atom_i, atom_j)
        atom_j_image = copy.deepcopy(atom_j)
        atom_j_image.frac_coord += image

        atom_i.cart_coord, atom_j_image.cart_coord = None, None
        atom_i.set_coord(lattice)
        atom_j_image.set_coord(lattice)

        return np.sum((atom_i.cart_coord - atom_j_image.cart_coord) ** 2) ** 0.5


class Atoms(Atom):
    """
        `Atoms class represent atom set in periodic solid system`

        @property
            formula:                chemical formula, <list>
            number:                 atomic number, <list>
            period:                 atomic period in element period table, <list>
            group:                  atomic group in element period table, <list>
            color:                  atomic color using RGB, <list>
            order:                  atomic order in <Structure class>, default: <list(range(len(formula)))>
            frac_coord:             fractional coordinates, <list>
            cart_coord:             cartesian coordinates, <list>
            _default_bonds:         atomic default bond property {atom: bond-length}

            count:          total atom number in atom set
            size:           list atom number according to their formula

        @func
            __initialize_attrs:     initialize the attributes from the element.yaml
            from_list:              construct the <class Atoms> from an Atom list, i.e., [Atom, Atom, Atom] --> Atoms
    """

    def __init__(self, *args, **kwargs):
        super(Atoms, self).__init__(*args, **kwargs)

        self.order = list(range(len(self.formula))) if isinstance(self.order, int) or None in self.order else self.order
        self.frac_coord = [None] * len(self.formula) if self.frac_coord is None else self.frac_coord
        self.cart_coord = [None] * len(self.formula) if self.cart_coord is None else self.cart_coord
        self.selective_matrix = [None] * len(self.formula) if self.selective_matrix is None else self.selective_matrix
        self.constrain = [False] * len(self.formula) if self.constrain is False else self.constrain
        self.spin = [0] * len(self.formula) if isinstance(self.spin, int) and self.spin == 0 else self.spin

        self.__index_list = []  # inner index-list
        self._atom_list = []  # static atoms-list

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
        return self.atom_list[index]

    def __deepcopy__(self, memo=None):
        atoms = Atoms(formula=self.formula, order=self.order, frac_coord=self.frac_coord, cart_coord=self.cart_coord,
                      selective_matrix=self.selective_matrix, constrain=self.constrain, spin=self.spin)
        atoms.coordination_number = self.coordination_number
        atoms.bonds = self.bonds
        atoms._atom_list = []
        return atoms

    @property
    def count(self) -> int:
        return len(self)

    @property
    def elements(self):
        return [(key, len(list(group))) for key, group in groupby(self.formula)]

    @property
    def size(self):
        return Counter(self.formula)

    @property
    def atom_list(self):  # atom may update, so we don't use a static list
        if not len(self._atom_list):
            for index in range(len(self.formula)):
                atom = Atom(formula=self.formula[index], order=self.order[index],
                            frac_coord=self.frac_coord[index], cart_coord=self.cart_coord[index],
                            selective_matrix=self.selective_matrix[index], constrain=self.constrain[index],
                            spin=self.spin[index])

                # update coordination number && bonds
                atom.coordination_number = self.coordination_number[
                    index] if self.coordination_number is not None else None
                atom.bonds = self.bonds[index] if len(self.bonds) != 0 else []
                self._atom_list.append(atom)

        return self._atom_list

    @property
    def atom_type(self):  # override this property
        return [f"{atom.formula}{atom.coordination_number}c" for atom in self]

    def set_coord(self, lattice: Lattice):  # overwrite this method
        assert lattice is not None
        if None not in self.cart_coord and None in self.frac_coord:
            self.frac_coord = np.dot(self.cart_coord, lattice.inverse)
        elif None not in self.frac_coord and None in self.cart_coord:
            self.cart_coord = np.dot(self.frac_coord, lattice.matrix)

        # update __atoms_list
        for index in range(len(self)):
            self.atom_list[index].frac_coord = self.frac_coord[index]
            self.atom_list[index].cart_coord = self.cart_coord[index]

        return self

    def perturb(self, lattice: Lattice, threshold=0.1, groups=9):
        """
        Perturb the atoms' coords

        @params:
            lattice:        Lattice type
            threshold:      max offset of atom
            groups:         how many groups you want to get
        """
        if None in self.cart_coord:
            self.set_coord(lattice=lattice)

        # group from z_value
        z_max, z_min = np.max(self.cart_coord[:, 2]), np.min(self.cart_coord[:, 2])
        group_np = np.linspace(z_min, z_max, groups + 1)
        group_index = []
        for index in range(groups):
            group_index.append(np.where((self.cart_coord[:, 2] >= group_np[index]) &
                                        (self.cart_coord[:, 2] <= group_np[index + 1])))

        # exponential decay
        decay = -np.linspace(0., (z_max - z_min) / 2, int(groups / 2))
        exp_decay = np.exp(decay) * threshold

        # construct perturb vector
        perturb_vector = np.empty(groups)
        perturb_vector[:int(groups / 2)] = exp_decay
        perturb_vector[-int(groups / 2):] = exp_decay[::-1]

        # construct perturb matrix
        perturb_matrix = np.empty((self.count, 3))
        for index, group in enumerate(group_index):
            perturb_matrix[group] = perturb_vector[index]

        random_normal = np.random.normal(loc=0., scale=0.01, size=(self.count, 3))
        perturb_item = perturb_matrix + random_normal

        # resolve fix_atom
        fix_item = np.where(self.selective_matrix == "F", 0, 1)
        perturb_item = perturb_item * fix_item

        self.cart_coord = self.cart_coord + perturb_item
        self.frac_coord = [None] * self.count
        self.set_coord(lattice=lattice)

        return self

    @staticmethod
    def from_list(atoms: list):
        formula = [atom.formula for atom in atoms]
        order: List[Any] = [atom.order for atom in atoms]
        frac_coord = [atom.frac_coord for atom in atoms]
        cart_coord = [atom.cart_coord for atom in atoms]
        selective_matrix = [atom.selective_matrix for atom in atoms]
        constrain = [atom.constrain for atom in atoms]
        spin = [atom.spin for atom in atoms]
        coordination_number = [atom.coordination_number for atom in atoms]
        bonds = [atom.bonds for atom in atoms]

        # update coordination number && bonds
        new_atoms = Atoms(formula=formula, order=order, frac_coord=frac_coord, cart_coord=cart_coord,
                          selective_matrix=selective_matrix, constrain=constrain, spin=spin)
        new_atoms.coordination_number = coordination_number
        new_atoms.bonds = bonds
        return new_atoms


if __name__ == '__main__':
    matrix = np.array([[15.414200, 0.000000, 0.000000], [-7.707100, 13.349089, 0.000000], [0.000000, 0.000000, 19.865999]])
    lattice = Lattice(matrix)
    print(matrix[1])
    atom_O=Atom('O', order= 0, frac_coord=None, cart_coord=None, selective_matrix=None,
                 constrain=False, spin=0)
    pass

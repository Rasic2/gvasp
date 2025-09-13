import logging

import numpy as np
import pytest

from gvasp.common.file import CONTCAR
from gvasp.common.base import Lattice

logger = logging.getLogger('TestLogger')


class TestLattice:
    def test_repr(self):
        lattice = Lattice(np.array([[7.707464, 0.000000, 0.000000],
                                    [-3.853732, 6.674860, 0.000000],
                                    [0.000000, 0.000000, 28.319031]]))
        logger.info(lattice)

    def test_from_POSCAR(self):
        Lattice.from_POSCAR('CONTCAR')


class TestAtom:
    atom_1 = CONTCAR('CONTCAR').structure.atoms[0]
    atom_2 = CONTCAR('CONTCAR').structure.atoms[1]

    def test_lt(self):
        logger.info(self.atom_1 < self.atom_2)

    def test_ge(self):
        logger.info(self.atom_1 >= self.atom_2)

    def test_repr(self):
        logger.info(self.atom_1)

    def test_atom_type(self):
        logger.info(self.atom_1.atom_type)


class TestAtoms:
    structure = CONTCAR('CONTCAR').structure
    atoms = structure.atoms

    def test_repr(self):
        logger.info(self.atoms)

    def test_contains(self):
        atom = self.atoms[0]
        logger.info(atom in self.atoms)

    def test_atom_type(self):
        logger.info(self.atoms.atom_type)

    def test_perturb(self):
        self.atoms.perturb(lattice=self.structure.lattice)


if __name__ == '__main__':
    pytest.main([__file__])

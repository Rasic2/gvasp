import itertools
import warnings
from multiprocessing import Pool as ProcessPool, cpu_count
from pathlib import Path

import numpy as np

from gvasp.common.base import Atom
from gvasp.common.error import PathNotExistError
from gvasp.common.structure import Structure
from gvasp.lib.path_cython import _get_funcs_and_forces as _get_funcs_and_forces_cython


class BasePath:

    def __new__(cls, *args, **kwargs):
        if cls is BasePath:
            raise TypeError(f'<{cls.__name__} class> may not be instantiated')
        return super().__new__(cls)

    def __init__(self):
        self.path = None

    def write(self):
        if not isinstance(self.path, list):
            raise PathNotExistError('structure path is not exist, please generate it first')

        for index, structure in enumerate(self.path):
            image_dir = f'{index:02d}'
            Path(image_dir).mkdir(exist_ok=True)
            structure.write_POSCAR(f'{image_dir}/POSCAR')


class LinearPath(BasePath):
    def __init__(self, ini_poscar, fni_poscar, images):
        super().__init__()
        self.ini_structure = Structure.from_POSCAR(ini_poscar)
        self.fni_structure = Structure.from_POSCAR(fni_poscar)
        self.images = images

    def run(self):
        assert self.ini_structure == self.fni_structure
        diff_image = (self.fni_structure - self.ini_structure) / (self.images + 1)

        image_structures = [self.ini_structure]
        for image in range(self.images):
            cart_coord = self.ini_structure.atoms.cart_coord + diff_image * (image + 1)
            image_structures.append(Structure.from_structure(self.ini_structure, cart_coord))

        image_structures.append(self.fni_structure)

        self.path = image_structures


class IdppPath(BasePath):

    def __init__(self, structures):
        """
        Initialize the IdppPath.

        Args:
            structures (list): Initial guess of the NEB path (including initial and final end-point structures).
        """
        super().__init__()

        lattice = structures[0].lattice
        atoms_num = structures[0].atoms.count
        images = len(structures) - 2
        target_dists = []

        # Initial guess of the path (in Cartesian coordinates) used in the IDPP algo.
        init_coords = []

        # Construct the set of target distance matrices via linear interpolation between those of end-point structures.
        pool = ProcessPool(processes=cpu_count())
        results = [pool.apply_async(structure.find_neighbour_table, args=(atoms_num, None, None, False, True)) for structure
                   in structures]
        structures = [item.get() for item in results]
        pool.close()
        pool.join()

        for i in range(1, images + 1):
            # Interpolated distance matrices
            dist = structures[0].neighbour_table.dist + i / (images + 1) * (
                    structures[-1].neighbour_table.dist - structures[0].neighbour_table.dist)

            target_dists.append(dist)

        target_dists = np.array(target_dists)

        # Set of translational vector matrices (antisymmetric) for the images.
        translations = np.zeros((images, atoms_num, atoms_num, 3), dtype=np.float64)

        # A set of weight functions. It is set as 1/d^4 for each image. Here, we take d as the average of the
        # target distance matrix and the actual distance matrix.
        weights = np.zeros_like(target_dists, dtype=np.float64)
        for ni in range(images):
            avg_dist = (target_dists[ni] + structures[ni + 1].neighbour_table.dist) / 2.0
            weights[ni] = 1.0 / (avg_dist ** 4 + np.eye(atoms_num, dtype=np.float64) * 1e-8)

        for ni, i in itertools.product(range(images + 2), range(atoms_num)):
            cart_coord = structures[ni].atoms[i].cart_coord
            init_coords.append(cart_coord)

            if ni not in [0, images + 1]:
                for j in range(i + 1, atoms_num):
                    img = Atom.search_image(structures[ni].atoms[i], structures[ni].atoms[j])
                    translations[ni - 1, i, j] = np.dot(img, lattice.matrix)
                    translations[ni - 1, j, i] = -np.dot(img, lattice.matrix)

        self.init_coords = np.array(init_coords).reshape((images + 2, atoms_num, 3))
        self.translations = translations
        self.weights = weights
        self.structures = structures
        self.target_dists = target_dists
        self.images = images

    @staticmethod
    def from_linear(ini_poscar, fni_poscar, images):
        linear_path = LinearPath(ini_poscar, fni_poscar, images)
        linear_path.run()
        return IdppPath(linear_path.path)

    def run(self, max_iter=1000, tol=1e-5, grad_tol=1e-3, step_size=0.05, max_disp=0.05, spring_const=5.0):
        """
        Perform iterative minimization of the set of objective functions in an NEB-like manner.
        In each iteration, the total force matrix for each image is constructed,
        which comprises both the spring forces and true forces.
        More details about the NEB approach can see Henkelman et al., J. Chem. Phys. 113, 9901 (2000).

        Args:
            max_iter (int): Maximum number of iterations in the minimization process.
            tol (float): Tolerance of the change of objective functions between consecutive steps.
            grad_tol (float): Tolerance of maximum force component (absolute value).
            step_size (float): Step size associated with the displacement ofn the atoms during the minimization process.
            max_disp (float): Maximum allowed atomic displacement in each iteration.
            spring_const (float): A virtual spring constant used in the NEB-like relaxation process.
        """

        coords = self.init_coords.copy()
        old_funcs = np.zeros((self.images,), dtype=np.float64)
        idpp_structures = [self.structures[0]]

        indices = list(range(len(self.structures[0].atoms)))

        # Iterative minimization
        for n in range(max_iter):
            # Get the sets of objective functions, true and total force matrices.
            funcs, true_forces = self._get_funcs_and_forces(coords)
            tot_forces = self._get_total_forces(coords, true_forces, spring_const=spring_const)

            # Each atom is allowed to move up to max_disp
            disp_mat = step_size * tot_forces[:, indices, :]
            disp_mat = np.where(np.abs(disp_mat) > max_disp, np.sign(disp_mat) * max_disp, disp_mat)
            coords[1: (self.images + 1), indices] += disp_mat

            max_force = np.abs(tot_forces[:, indices, :]).max()
            tot_res = np.sum(np.abs(old_funcs - funcs))

            if tot_res < tol and max_force < grad_tol:
                break

            old_funcs = funcs
        else:
            warnings.warn('Maximum iteration number is reached without convergence!', UserWarning)

        for ni in range(self.images):
            # generate the improved image structure
            image_structure = self.structures[ni + 1]
            cart_coords = coords[ni + 1]

            new_image_structure = Structure.from_structure(image_structure, cart_coords)
            idpp_structures.append(new_image_structure)

        idpp_structures.append(self.structures[-1])
        self.path = idpp_structures

    def _get_funcs_and_forces(self, x):
        """
        Calculate the set of objective functions as well as their gradients, i.e. "effective true forces"
        """
        trans = self.translations
        weights = self.weights
        target_dists = self.target_dists

        funcs, funcs_prime = _get_funcs_and_forces_cython(x, trans, weights, target_dists)

        return 0.5 * np.array(funcs), -2 * np.array(funcs_prime)

    @staticmethod
    def _get_unit_vector(vec):
        """
        Calculate the unit vector of a vector.

        Args:
            vec: Vector.
        """
        return vec / np.sqrt(np.sum(vec ** 2))

    def _get_total_forces(self, x, true_forces, spring_const):
        """
        Calculate the total force on each image structure, which is equal to
        the spring force along the tangent + true force perpendicular to the
        tangent. Note that the spring force is the modified version in the
        literature (e.g. Henkelman et al., J. Chem. Phys. 113, 9901 (2000)).
        """

        total_forces = []
        atoms_num = np.shape(true_forces)[1]

        for ni in range(1, len(x) - 1):
            vec1 = (x[ni + 1] - x[ni]).flatten()
            vec2 = (x[ni] - x[ni - 1]).flatten()

            # Local tangent
            tangent = self._get_unit_vector(vec1) + self._get_unit_vector(vec2)
            tangent = self._get_unit_vector(tangent)

            # Spring force
            spring_force = spring_const * (np.linalg.norm(vec1) - np.linalg.norm(vec2)) * tangent

            # Total force
            flat_ft = true_forces[ni - 1].copy().flatten()
            total_force = true_forces[ni - 1] + (spring_force - np.dot(flat_ft, tangent) * tangent).reshape(atoms_num,
                                                                                                            3)
            total_forces.append(total_force)

        return np.array(total_forces)

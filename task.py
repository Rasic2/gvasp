import copy
from pathlib import Path

from pymatgen.core import Structure as pmg_Structure
from pymatgen_diffusion.neb.pathfinder import IDPPSolver

from file import POSCAR
from logger import logger
from structure import Structure


class NEBCal(object):
    def __init__(self, ini_POSCAR, fni_POSCAR, images=4):
        self.ini_POSCAR = ini_POSCAR
        self.fni_POSCAR = fni_POSCAR
        self.images = images

    def generate(self, method="liner"):
        if method == "idpp":
            self._generate_idpp()
        elif method == "liner":
            self._generate_liner()
        else:
            raise NotImplementedError(f"{method} has not been implemented for NEB task")

    def _generate_idpp(self):
        """
        Generate NEB-task images by idpp method (J. Chem. Phys. 140, 214106 (2014))
        """
        ini_structure = pmg_Structure.from_file(self.ini_POSCAR, False)
        fni_structure = pmg_Structure.from_file(self.fni_POSCAR, False)
        obj = IDPPSolver.from_endpoints(endpoints=[ini_structure, fni_structure], nimages=self.images, sort_tol=1.0)
        path = obj.run(maxiter=5000, tol=1e-5, gtol=1e-3, step_size=0.05, max_disp=0.05, spring_const=5.0)

        for image in range(len(path)):
            image_dir = f"{image:02d}"
            Path(f"{image_dir}").mkdir(exist_ok=True)
            POSCAR_file = f"{image_dir}/POSCAR"
            path[image].to(fmt="poscar", filename=POSCAR_file)
        logger.info("Improved interpolation of NEB initial guess has been generated.")

    def _generate_liner(self):
        """
        Generate NEB-task images by linear interpolation method
        """
        ini_structure = POSCAR(self.ini_POSCAR).structure
        fni_structure = POSCAR(self.fni_POSCAR).structure
        assert ini_structure == fni_structure, f"{self.ini_POSCAR} and {self.fni_POSCAR} are not structure match"
        diff_image = (fni_structure - ini_structure) / (self.images + 1)

        # write ini-structure
        ini_dir = f"{00:02d}"
        Path(ini_dir).mkdir(exist_ok=True)
        ini_structure.write(f"{ini_dir}/POSCAR")

        # write fni-structure
        fni_dir = f"{self.images + 1:02d}"
        Path(fni_dir).mkdir(exist_ok=True)
        fni_structure.write(f"{fni_dir}/POSCAR")

        # resolve and write image-structures
        for image in range(self.images):
            image_dir = f"{image + 1:02d}"
            Path(image_dir).mkdir(exist_ok=True)
            image_atoms = copy.deepcopy(ini_structure.atoms)
            image_atoms.frac_coord = [None] * len(image_atoms)
            image_atoms.cart_coord = ini_structure.atoms.cart_coord + diff_image * (image + 1)
            image_atoms.set_coord(ini_structure.lattice)
            image_structure = Structure(atoms=image_atoms, lattice=ini_structure.lattice)
            image_structure.write(f"{image_dir}/POSCAR")
        logger.info("Linear interpolation of NEB initial guess has been generated.")

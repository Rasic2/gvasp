import copy
import os
from pathlib import Path

from matplotlib import pyplot as plt
from pymatgen.core import Structure as pmg_Structure
from pymatgen_diffusion.neb.pathfinder import IDPPSolver

from common.figure import Figure, plot_wrapper, PchipLine
from common.file import POSCAR, OUTCAR, XDATCAR, ARCFile
from common.logger import logger
from common.structure import Structure


class NEBCal(Figure):
    def __init__(self, ini_POSCAR=None, fni_POSCAR=None, images=4, xlabel="Distance (Å)", ylabel="Energy (eV)",
                 width=10):
        super(NEBCal, self).__init__(xlabel=xlabel, ylabel=ylabel, width=width)
        self.ini_POSCAR = ini_POSCAR
        self.fni_POSCAR = fni_POSCAR
        self.images = images

    def generate(self, method="liner", check_overlap=True):
        """
        Generate NEB-task images && check their structure overlap
        """
        if method == "idpp":
            self._generate_idpp()
        elif method == "liner":
            self._generate_liner()
        else:
            raise NotImplementedError(f"{method} has not been implemented for NEB task")

        if check_overlap:
            self._check_overlap()

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

    @staticmethod
    def _search_neb_dir():
        neb_dirs = []

        for dir in Path(os.getcwd()).iterdir():
            if Path(dir).is_dir() and Path(dir).stem.isdigit():
                neb_dirs.append(dir)
        return neb_dirs

    def _check_overlap(self):
        logger.info("Check structures overlap")
        neb_dirs = NEBCal._search_neb_dir()

        for image in neb_dirs:
            structure = POSCAR(Path(f"{image}/POSCAR")).structure
            logger.info(f"check {image.stem} dir...")
            structure.check_overlap()

        logger.info("All structures don't have overlap")

    @staticmethod
    def monitor():
        """
        Monitor tangent, energy and barrier in the NEB-task
        """
        neb_dirs = NEBCal._search_neb_dir()
        ini_energy = 0.
        print("image   tangent          energy       barrier")
        for image in neb_dirs:
            outcar = OUTCAR(f"{image}/OUTCAR")
            if not int(image.stem):
                ini_energy = outcar.last_energy
            barrier = outcar.last_energy - ini_energy
            print(f" {image.stem} \t {outcar.last_tangent:>10.6f} \t {outcar.last_energy} \t {barrier:.6f}")

    @plot_wrapper
    def plot(self, color="#ed0345"):
        neb_dirs = NEBCal._search_neb_dir()
        dists = []
        energy = []
        ini_energy = 0.
        for image in neb_dirs:
            posfile = "CONTCAR" if Path(f"{image}/CONTCAR").exists() else "POSCAR"
            outcar = OUTCAR(f"{image}/OUTCAR")
            structure = POSCAR(f"{image}/{posfile}").structure
            if not int(image.stem):
                ini_energy = outcar.last_energy
                ini_structure = structure

            dists.append(Structure.dist(structure, ini_structure))
            energy.append(outcar.last_energy - ini_energy)

        plt.plot(dists, energy, "o")
        PchipLine(x=dists, y=energy, color=color, linewidth=2)()

    @staticmethod
    def movie(name="movie.arc", file="CONTCAR"):
        """
        Generate *.arc file from images/[POSCAR|CONTCAR] files
        """
        neb_dirs = NEBCal._search_neb_dir()
        structures = []

        for image in neb_dirs:
            posfile = "CONTCAR" if file == "CONTCAR" and Path(f"{image}/CONTCAR").exists() else "POSCAR"
            structures.append(POSCAR(f"{image}/{posfile}").structure)

        ARCFile.write(name=name, structure=structures, lattice=structures[0].lattice)

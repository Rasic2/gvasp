from pathlib import Path

from pymatgen.core import Structure
from pymatgen_diffusion.neb.pathfinder import IDPPSolver

from logger import logger


class NEBCal(object):
    def __init__(self, ini_POSCAR, fni_POSCAR, images=4):
        self.ini_POSCAR = ini_POSCAR
        self.fni_POSCAR = fni_POSCAR
        self.images = images

    def generate(self, method="idpp"):
        if method == "idpp":
            ini_structure = Structure.from_file(self.ini_POSCAR, False)
            fni_structure = Structure.from_file(self.fni_POSCAR, False)
            obj = IDPPSolver.from_endpoints(endpoints=[ini_structure, fni_structure], nimages=self.images, sort_tol=1.0)
            path = obj.run(maxiter=5000, tol=1e-5, gtol=1e-3, step_size=0.05, max_disp=0.05, spring_const=5.0)

            for image in range(len(path)):
                image_dir = f"{image:02d}"
                Path(f"{image_dir}").mkdir(exist_ok=True)
                POSCAR_file = f"{image_dir}/POSCAR"
                path[image].to(fmt="poscar", filename=POSCAR_file)
            logger.info("Improved interpolation of NEB initial guess has been generated.")

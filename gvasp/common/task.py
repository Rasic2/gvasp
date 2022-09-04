import abc
from functools import wraps
from pathlib import Path

import numpy as np
import yaml

from gvasp.common.base import Atom
from gvasp.common.error import XSDFileNotFoundError, TooManyXSDFileError, ConstrainError
from gvasp.common.file import POSCAR, OUTCAR, ARCFile, XSDFile, KPOINTS, POTCAR, XDATCAR, CHGCAR, AECCAR0, AECCAR2, \
    CHGCAR_mag, INCAR
from gvasp.common.logger import Logger
from gvasp.common.setting import WorkDir, ConfigManager
from gvasp.neb.path import IdppPath, LinearPath

Red = "\033[1;31m"
Green = "\033[1;32m"
Yellow = "\033[1;33m"
Blue = "\033[1;34m"
Purple = "\033[1;35m"
Cyan = "\033[1;36m"
Reset = "\033[0m"


def write_wrapper(func):
    @wraps(func)
    def wrapper(self):
        func(self)
        self.incar.write(name="INCAR")

    return wrapper


class BaseTask(metaclass=abc.ABCMeta):
    """
    Task Base class, load config.json, generate INCAR, KPOINTS, POSCAR and POTCAR
    Note: subclass should have `generate` method
    """
    Template, PotDir, Scheduler = ConfigManager().template, ConfigManager().potdir, ConfigManager().scheduler
    with open(ConfigManager().UValue) as f:
        UValue = yaml.safe_load(f.read())

    def __init__(self):
        self.title = None
        self.structure = None
        self.elements = None

        # set INCAR template
        self._incar = self.Template if self._search_suffix(".incar") is None else self._search_suffix(".incar")
        self.incar = INCAR(self._incar)

        # set submit template
        self.submit = self.Scheduler if self._search_suffix(".submit") is None else self._search_suffix(".submit")

    def get_all_parents(self):
        def get_parent(path: Path):
            parent = path.parent
            if path != parent:
                yield path
                yield from get_parent(parent)
            else:
                yield path

        return [path for path in get_parent(WorkDir.absolute())]

    def _search_suffix(self, suffix):
        for directory in self.get_all_parents():
            for file in directory.iterdir():
                if file.is_file() and file.name.endswith(f"{suffix}"):
                    return file
        else:
            return

    @abc.abstractmethod
    def generate(self, potential: (str, list)):
        """
        generate main method, subclass should inherit or overwrite
        """
        self._generate_POSCAR()
        self._generate_KPOINTS()
        self._generate_POTCAR(potential=potential)
        self._generate_INCAR()
        self._generate_submit()

        print(f"---------------general info (#{self.__class__.__name__})-----------------------")
        print(f"Elements    Total  Relax   potential orbital UValue")
        potential = [potential] * len(self.elements) if isinstance(potential, str) else potential
        index = 0
        for element, p in zip(self.elements, potential):
            element_index = [index for index, formula in enumerate(self.structure.atoms.formula) if formula == element]
            element_tf = np.sum(
                np.sum(self.structure.atoms.selective_matrix[element_index] == ["T", "T", "T"], axis=1) == 3)
            print(f"{element:^10s}"
                  f"{self.structure.atoms.size[element]:>6d}"
                  f"{element_tf:>6d}(T)   "
                  f"{p}    "
                  f"{self.incar.LDAUL[index]}     "
                  f"{self.incar.LDAUU[index] - self.incar.LDAUJ[index]}")
            index += 1
        print()
        print(f"KPoints: {KPOINTS.min_number(lattice=self.structure.lattice)}")
        print()
        print(f"{Red}Job Name: {self.title}{Reset}")
        print(f"{Yellow}INCAR template: {self._incar}{Reset}")
        print(f"{Cyan}Submit template: {self.submit}{Reset}")
        print(f"------------------------------------------------------------------")

    def _generate_INCAR(self):
        """
        generate by copy incar_template, modify the +U parameters
        """
        logger = Logger().logger
        if self.incar.LDAU:
            LDAUL, LDAUU, LDAUJ = [], [], []
            for element in self.elements:
                if self.UValue.get(f'Element {element}', None) is not None:
                    LDAUL.append(self.UValue[f'Element {element}']['orbital'])
                    LDAUU.append(self.UValue[f'Element {element}']['U'])
                    LDAUJ.append(self.UValue[f'Element {element}']['J'])
                else:
                    LDAUL.append(-1)
                    LDAUU.append(0.0)
                    LDAUJ.append(0.0)
                    logger.warning(f"{element} not found in UValue, +U parameters set default: LDAUL = -1, "
                                   f"LDAUU = 0.0, "
                                   f"LDAUJ = 0.0")

            self.incar.LDAUL = LDAUL
            self.incar.LDAUU = LDAUU
            self.incar.LDAUJ = LDAUJ
            self.incar.LMAXMIX = 6 if 3 in self.incar.LDAUL else 4

    def _generate_KPOINTS(self):
        """
        generate KPOINTS, Gamma-centered mesh, number is autogenerated
        """
        with open("KPOINTS", "w") as f:
            f.write("AutoGenerated \n")
            f.write("0 \n")
            f.write("Gamma \n")
            f.write(f"{' '.join(list(map(str, KPOINTS.min_number(lattice=self.structure.lattice))))} \n")
            f.write("0 0 0 \n")

    def _generate_POSCAR(self, *args, **kargs):
        """
        generate POSCAR from only one *.xsd file, and register `self.structure` and `self.elements`
        """
        xsd_files = list(WorkDir.glob("*.xsd"))
        if not len(xsd_files):
            raise XSDFileNotFoundError("*.xsd file is not found, please check workdir")
        elif len(xsd_files) > 1:
            raise TooManyXSDFileError("exist more than one *.xsd file, please check workdir")

        xsd_file = XSDFile(xsd_files[0])
        self.title = xsd_file.name.stem
        self.structure = xsd_file.structure
        self.elements = list(self.structure.atoms.size.keys())
        self.structure.write_POSCAR(name="POSCAR")

    def _generate_POTCAR(self, potential):
        """
         generate POTCAR automatically, call the `cat` method of POTCAR
         """
        potcar = POTCAR.cat(potentials=potential, elements=self.elements, potdir=self.PotDir)
        potcar.write(name="POTCAR")

    def _generate_submit(self):
        """
         generate job.submit automatically
         """
        with open(self.submit, "r") as f:
            content = f.readlines()

        with open("submit.script", "w") as g:
            for line in content:
                if line.startswith("#SBATCH -J"):
                    g.write(f"#SBATCH -J {self.title} \n")
                else:
                    g.write(line)


class Animatable(metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    def movie(name):
        """
        make arc file to visualize the optimization steps
        """
        XDATCAR("XDATCAR").movie(name=name)


class OptTask(BaseTask, Animatable):
    """
    Optimization task manager, subclass of BaseTask
    """

    def generate(self, potential="PAW_PBE"):
        """
        fully inherit BaseTask's generate
        """
        super(OptTask, self).generate(potential=potential)

    @write_wrapper
    def _generate_INCAR(self):
        """
        Inherit BaseTask's _generate_INCAR, but add wrapper to write INCAR
        """
        super(OptTask, self)._generate_INCAR()

    @staticmethod
    def movie(name="movie.arc"):
        """
        fully inherit BaseTask's movie
        """
        Animatable.movie(name=name)


class ChargeTask(BaseTask):
    """
    Charge calculation task manager, subclass of BaseTask
    """

    def generate(self, potential="PAW_PBE"):
        """
        fully inherit BaseTask's generate
        """
        super(ChargeTask, self).generate(potential=potential)

    @write_wrapper
    def _generate_INCAR(self):
        """
        Inherit BaseTask's _generate_INCAR, modify parameters and write to INCAR
        parameters setting:
            IBRION = 1
            LAECHG = .TRUE.
            LCHARG = .TRUE.
        """
        super(ChargeTask, self)._generate_INCAR()
        self.incar.IBRION = 1
        self.incar.LAECHG = True
        self.incar.LCHARG = True

    @staticmethod
    def split():
        """
        split CHGCAR to CHGCAR_tot && CHGCAR_mag
        """
        CHGCAR("CHGCAR").split()

    @staticmethod
    def sum():
        """
        sum AECCAR0 and AECCAR2 to CHGCAR_sum
        """
        aeccar0 = AECCAR0("AECCAR0")
        aeccar2 = AECCAR2("AECCAR2")
        chgcar_sum = aeccar0 + aeccar2
        chgcar_sum.write()

    @staticmethod
    def to_grd(name="vasp.grd", Dencut=250):
        """
        transform CHGCAR_mag to grd file
        """
        CHGCAR_mag("CHGCAR_mag").to_grd(name=name, DenCut=Dencut)


class DOSTask(BaseTask):
    """
    Density of States (DOS) calculation task manager, subclass of BaseTask
    """

    def generate(self, potential="PAW_PBE"):
        """
        fully inherit BaseTask's generate
        """
        super(DOSTask, self).generate(potential=potential)

    @write_wrapper
    def _generate_INCAR(self):
        """
        Inherit BaseTask's _generate_INCAR, modify parameters and write to INCAR
        parameters setting:
            ISTART = 1
            ICHARG = 11
            IBRION = -1
            NSW = 1
            LORBIT = 12
            NEDOS = 2000
        """
        super(DOSTask, self)._generate_INCAR()
        self.incar.ISTART = 1
        self.incar.ICHARG = 11
        self.incar.IBRION = -1
        self.incar.NSW = 1
        self.incar.LORBIT = 12
        self.incar.NEDOS = 2000


class FreqTask(BaseTask, Animatable):
    """
    Frequency calculation task manager, subclass of BaseTask
    """

    def generate(self, potential="PAW_PBE"):
        """
        fully inherit BaseTask's generate
        """
        super(FreqTask, self).generate(potential=potential)

    @write_wrapper
    def _generate_INCAR(self):
        """
        Inherit BaseTask's _generate_INCAR, modify parameters and write to INCAR
        parameters setting:
            IBRION = 5
            ISYM = 0
            NSW = 1
            NFREE = 2
            POTIM = 0.015
        """
        super(FreqTask, self)._generate_INCAR()
        self.incar.IBRION = 5
        self.incar.ISYM = 0
        self.incar.NSW = 1
        self.incar.NFREE = 2
        self.incar.POTIM = 0.015

    @staticmethod
    def movie(freq="image"):
        """
        visualize the frequency vibration, default: image
        """
        outcar = OUTCAR("OUTCAR")
        outcar.animation_freq(freq=freq)


class MDTask(BaseTask, Animatable):
    """
     ab-initio molecular dynamics (AIMD) calculation task manager, subclass of BaseTask
     """

    def generate(self, potential="PAW_PBE"):
        """
        fully inherit BaseTask's generate
        """
        super(MDTask, self).generate(potential=potential)

    @write_wrapper
    def _generate_INCAR(self):
        """
        Inherit BaseTask's _generate_INCAR, modify parameters and write to INCAR
        parameters setting:
            IBRION = 0
            NSW = 100000
            POTIM = 0.5
            SMASS = 2.
            MDALGO = 2
            TEBEG = 300.
            TEEND = 300.
        """
        super(MDTask, self)._generate_INCAR()
        self.incar.IBRION = 0
        self.incar.NSW = 100000
        self.incar.POTIM = 0.5
        self.incar.SMASS = 2.
        self.incar.MDALGO = 2
        self.incar.TEBEG = 300.
        self.incar.TEEND = 300.

    @staticmethod
    def movie(name="movie.arc"):
        """
        fully inherit BaseTask's movie
        """
        super().movie(name=name)


class STMTask(BaseTask):
    """
     Scanning Tunneling Microscope (STM) image modelling calculation task manager, subclass of BaseTask
     """

    def generate(self, potential="PAW_PBE"):
        """
        fully inherit BaseTask's generate
        """
        super(STMTask, self).generate(potential=potential)

    @write_wrapper
    def _generate_INCAR(self):
        """
        Inherit BaseTask's _generate_INCAR, modify parameters and write to INCAR
        parameters setting:
            ISTART = 1
            IBRION = -1
            NSW = 0
            LPARD = .TRUE.
            NBMOD = -3
            EINT = 5.
            LSEPB = .FALSE.
            LSEPK = .FALSE.
        """
        super(STMTask, self)._generate_INCAR()
        self.incar.ISTART = 1
        self.incar.IBRION = -1
        self.incar.NSW = 0
        self.incar.LPARD = True
        self.incar.NBMOD = -3
        self.incar.EINT = 5.
        self.incar.LSEPB = False
        self.incar.LSEPK = False


class ConTSTask(BaseTask, Animatable):
    """
     Constrain transition state (Con-TS) calculation task manager, subclass of BaseTask
     """

    def generate(self, potential="PAW_PBE"):
        """
        fully inherit BaseTask's generate
        """
        super(ConTSTask, self).generate(potential=potential)
        self._generate_fort()

    @write_wrapper
    def _generate_INCAR(self):
        """
        Inherit BaseTask's _generate_INCAR, modify parameters and write to INCAR
        parameters setting:
            IBRION = 1
        """
        super(ConTSTask, self)._generate_INCAR()
        self.incar.IBRION = 1

    def _generate_fort(self):
        constrain_atom = [atom for atom in self.structure.atoms if atom.constrain]
        if len(constrain_atom) != 2:
            raise ConstrainError("Number of constrain atoms should equal to 2")

        distance = Atom.distance(constrain_atom[0], constrain_atom[1], lattice=self.structure.lattice)
        with open("fort.188", "w") as f:
            f.write("1 \n")
            f.write("3 \n")
            f.write("6 \n")
            f.write("3 \n")
            f.write("0.03 \n")
            f.write(f"{constrain_atom[0].order + 1} {constrain_atom[1].order + 1} {distance:.4f}\n")
            f.write("0 \n")

        print(f"Constrain Information: {constrain_atom[0].order + 1}-{constrain_atom[1].order + 1}, "
              f"distance = {distance:.4f}")

    @staticmethod
    def movie(name="movie.arc"):
        """
        fully inherit BaseTask's movie
        """
        super().movie(name=name)


class NEBTask(BaseTask, Animatable):
    """
     Nudged Elastic Band (NEB) calculation (no-climbing) task manager, subclass of BaseTask
     """

    def __init__(self, ini_poscar=None, fni_poscar=None, images=4):
        super(NEBTask, self).__init__()

        self.ini_poscar = ini_poscar
        self.fni_poscar = fni_poscar
        self.images = images

        self.structure = POSCAR(self.ini_poscar).structure
        self.elements = list(zip(*self.structure.atoms.elements))[0]

    @staticmethod
    def sort(ini_poscar, fni_poscar):
        """
        Tailor the atoms' order for neb task

        @param:
            ini_poscar:   initial POSCAR file name
            fni_poscar:   final POSCAR file name
        """
        POSCAR.align(ini_poscar, fni_poscar)

    def generate(self, method="linear", check_overlap=True, potential="PAW_PBE"):
        """
        Overwrite BaseTask's generate, add `method` and `check_overlap` parameters
        """
        self._generate_POSCAR(method=method, check_overlap=check_overlap)
        self._generate_KPOINTS()
        self._generate_POTCAR(potential=potential)
        self._generate_INCAR()

    @write_wrapper
    def _generate_INCAR(self):
        """
        Inherit BaseTask's _generate_INCAR, modify parameters and write to INCAR
        parameters setting:
            IBRION = 3
            POTIM = 0.
            SPRING = -5.
            LCLIMB = .FALSE.
            ICHAIN = 0
            IOPT = 3
            MAXMOVE = 0.03
            IMAGES =
        """
        super(NEBTask, self)._generate_INCAR()
        self.incar.IBRION = 3
        self.incar.POTIM = 0.
        self.incar.SPRING = -5.
        self.incar.LCLIMB = False
        self.incar.ICHAIN = 0
        self.incar.IOPT = 3
        self.incar.MAXMOVE = 0.03
        self.incar.IMAGES = self.images

    def _generate_POSCAR(self, method, check_overlap):
        """
        Generate NEB-task images && check their structure overlap
        """
        if method == "idpp":
            self._generate_idpp()
        elif method == "linear":
            self._generate_liner()
        else:
            raise NotImplementedError(f"{method} has not been implemented for NEB task")

        if check_overlap:
            NEBTask._check_overlap()

    def _generate_idpp(self):
        """
        Generate NEB-task images by idpp method (J. Chem. Phys. 140, 214106 (2014))
        """
        logger = Logger().logger

        idpp_path = IdppPath.from_linear(self.ini_poscar, self.fni_poscar, self.images)
        idpp_path.run()
        idpp_path.write()

        logger.info("Improved interpolation of NEB initial guess has been generated.")

    def _generate_liner(self):
        """
        Generate NEB-task images by linear interpolation method
        """
        logger = Logger().logger

        linear_path = LinearPath(self.ini_poscar, self.fni_poscar, self.images)
        linear_path.run()
        linear_path.write()

        logger.info("Linear interpolation of NEB initial guess has been generated.")

    @staticmethod
    def _search_neb_dir(workdir=None):
        """
        Search neb task directories from workdir
        """
        if workdir is None:
            workdir = WorkDir

        neb_dirs = []

        for directory in workdir.iterdir():
            if Path(directory).is_dir() and Path(directory).stem.isdigit():
                neb_dirs.append(directory)
        return sorted(neb_dirs)

    @staticmethod
    def _check_overlap():
        """
        Check if two atoms' distance is too small, (following may add method to tailor their distances)
        """
        logger = Logger().logger
        logger.info("Check structures overlap")
        neb_dirs = NEBTask._search_neb_dir()

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
        neb_dirs = NEBTask._search_neb_dir()
        ini_energy = 0.
        print("image   tangent          energy       barrier")
        for image in neb_dirs:
            outcar = OUTCAR(f"{image}/OUTCAR")
            if not int(image.stem):
                ini_energy = outcar.last_energy
            barrier = outcar.last_energy - ini_energy
            print(f" {image.stem} \t {outcar.last_tangent:>10.6f} \t {outcar.last_energy} \t {barrier:.6f}")

    @staticmethod
    def movie(name="movie.arc", file="CONTCAR", workdir=None):
        """
        Generate arc file from images/[POSCAR|CONTCAR] files
        """
        neb_dirs = NEBTask._search_neb_dir(workdir)
        structures = []

        for image in neb_dirs:
            posfile = "CONTCAR" if file == "CONTCAR" and Path(f"{image}/CONTCAR").exists() else "POSCAR"
            structures.append(POSCAR(f"{image}/{posfile}").structure)

        ARCFile.write(name=name, structure=structures, lattice=structures[0].lattice)


class DimerTask(BaseTask, Animatable):
    def generate(self, potential="PAW_PBE"):
        """
        fully inherit BaseTask's generate
        """
        super(DimerTask, self).generate(potential=potential)

    @write_wrapper
    def _generate_INCAR(self):
        """
        Inherit BaseTask's _generate_INCAR, modify parameters and write to INCAR
        parameters setting:
            IBRION = 3
            POTIM = 0.
            ISYM = 0
            ICHAIN = 2
            DdR = 0.005
            DRotMax = 10
            DFNMax = 1.
            DFNMin = 0.01
            IOPT = 2     
        """
        super(DimerTask, self)._generate_INCAR()
        self.incar.IBRION = 3
        self.incar.POTIM = 0.
        self.incar.ISYM = 0
        self.incar.ICHAIN = 2
        self.incar.DdR = 0.005
        self.incar.DRotMax = 10
        self.incar.DFNMax = 1.
        self.incar.DFNMin = 0.01
        self.incar.IOPT = 2

    @staticmethod
    def movie(name="movie.arc"):
        super().movie(name=name)

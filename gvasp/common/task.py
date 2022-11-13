import abc
import logging
import os
import shutil
from functools import wraps
from pathlib import Path

import numpy as np
import yaml
from seekpath import get_path

from gvasp.common.base import Atom
from gvasp.common.constant import GREEN, YELLOW, RESET, RED
from gvasp.common.error import XSDFileNotFoundError, TooManyXSDFileError, ConstrainError
from gvasp.common.file import POSCAR, OUTCAR, ARCFile, XSDFile, KPOINTS, POTCAR, XDATCAR, CHGCAR, AECCAR0, AECCAR2, \
    CHGCAR_mag, INCAR, SubmitFile, CONTCAR
from gvasp.common.setting import WorkDir, ConfigManager
from gvasp.neb.path import IdppPath, LinearPath

logger = logging.getLogger(__name__)


def write_wrapper(func):
    @wraps(func)
    def wrapper(self, *args, **kargs):
        func(self, *args, **kargs)
        self.incar.write(name="INCAR")

    return wrapper


def end_symbol(func):
    @wraps(func)
    def wrapper(self, *args, **kargs):
        func(self, *args, **kargs)
        if kargs.get("print_end", True):
            print(f"------------------------------------------------------------------")

    return wrapper


class BaseTask(metaclass=abc.ABCMeta):
    """
    Task Base class, load config.json, generate INCAR, KPOINTS, POSCAR and POTCAR
    Note: subclass should have `generate` method
    """
    Template, PotDir, Scheduler = ConfigManager().template, ConfigManager().potdir, ConfigManager().scheduler
    UValueBase = ConfigManager().UValue

    def __init__(self):
        self.title = None
        self.structure = None
        self.elements = None
        self.valence = None

        # set INCAR template
        self._incar = self.Template if self._search_suffix(".incar") is None else self._search_suffix(".incar")
        self.incar = INCAR(self._incar)

        # set UValue template
        self.UValuePath = self.UValueBase if self._search_suffix(".uvalue") is None else self._search_suffix(".uvalue")
        with open(self.UValuePath) as f:
            self.UValue = yaml.safe_load(f.read())

        # set submit template
        self.submit = self.Scheduler if self._search_suffix(".submit") is None else self._search_suffix(".submit")
        self.finish = None

    @staticmethod
    def get_all_parents():
        def get_parent(path: Path):
            parent = path.parent
            if path != parent:
                yield path
                yield from get_parent(parent)
            else:
                yield path

        return [path for path in get_parent(WorkDir.absolute())]

    @staticmethod
    def _search_suffix(suffix):
        """
        Search file with the special suffix in all parents directories

        Args:
            suffix (str): specify the suffix

        Returns:
            file (Path): file path with the special suffix
        """
        for directory in BaseTask.get_all_parents():
            try:
                for file in directory.iterdir():
                    try:
                        if file.is_file() and file.name.endswith(f"{suffix}"):
                            return file
                    except PermissionError:
                        continue
            except PermissionError:
                continue
        else:
            return

    @end_symbol
    @abc.abstractmethod
    def generate(self, potential: (str, list), continuous=False, vdw=False, sol=False, gamma=False, nelect=None,
                 mag=False):
        """
        generate main method, subclass should inherit or overwrite
        """
        if continuous:
            self._generate_cdir()
        self._generate_POSCAR(continuous=continuous)
        self._generate_KPOINTS(gamma=gamma)
        self._generate_POTCAR(potential=potential)
        self._generate_INCAR(vdw=vdw, sol=sol, nelect=nelect, mag=mag)
        self._generate_submit(gamma=gamma)
        self._generate_info(potential=potential, gamma=gamma)

    def _generate_cdir(self, dir=None, files=None):
        Path(dir).mkdir(exist_ok=True)
        for file in files:
            shutil.copy(file, dir)
        os.chdir(dir)
        self.incar = INCAR("INCAR")

    def _generate_info(self, potential, gamma):
        """
        generate short information
        """
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
                  f"{self.incar.LDAUL[index]:>2d}     "
                  f"{self.incar.LDAUU[index] - self.incar.LDAUJ[index]}")
            index += 1
        print()
        if gamma:
            print(f"KPoints: [1 1 1]")
        elif self.__class__.__name__ == "BandTask":
            print(f"KPoints: line-mode for band structure")
        else:
            print(f"KPoints: {KPOINTS.min_number(structure=self.structure)}")
        print()
        print(f"{GREEN}Job Name: {self.title}{RESET}")
        print(f"{YELLOW}INCAR template: {self._incar}{RESET}")
        print(f"{YELLOW}UValue template: {self.UValuePath}{RESET}")
        print(f"{YELLOW}Submit template: {self.submit}{RESET}")

        if getattr(self.incar, "IVDW", None) is not None:
            print(f"{RED}--> VDW-correction: IVDW = {self.incar.IVDW}{RESET}")

        if getattr(self.incar, "LSOL", None) is not None:
            print(f"{RED}--> Solvation calculation{RESET}")

        if getattr(self.incar, "NELECT", None) is not None:
            print(f"{RED}--> Charged system, NELECT = {self.incar.NELECT}{RESET}")

        if gamma:
            print(f"{RED}--> Gamma-point calculation{RESET}")

    def _generate_INCAR(self, vdw, sol, nelect, mag=False):
        """
        generate by copy incar_template, modify the +U parameters
        """
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

        if vdw:
            self.incar.IVDW = 12

        if sol:
            self.incar.LSOL = True  # only consider water, not set EB_K

        if nelect is not None:
            t_valence = sum([num * valence for (_, num), valence in zip(self.structure.atoms.elements, self.valence)])
            self.incar.NELECT = t_valence + float(nelect)

        if mag:
            self.incar.MAGMOM = list(self.structure.atoms.spin)

    def _generate_KPOINTS(self, gamma):
        """
        generate KPOINTS, Gamma-centered mesh, number is autogenerated
        """
        with open("KPOINTS", "w") as f:
            f.write("AutoGenerated \n")
            f.write("0 \n")
            f.write("Gamma \n")
            if gamma:
                f.write(f"1 1 1 \n")
            else:
                f.write(f"{' '.join(list(map(str, KPOINTS.min_number(structure=self.structure))))} \n")
            f.write("0 0 0 \n")

    def _generate_POSCAR(self, continuous, method=None, check_overlap=None):
        """
        generate POSCAR from only one *.xsd file, and register `self.structure` and `self.elements`
        """
        if not continuous:
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
        else:
            self.title = f"continuous-{self.__class__.__name__}"
            self.structure = CONTCAR("CONTCAR").structure
            self.elements = list(self.structure.atoms.size.keys())
            self.structure.write_POSCAR(name="POSCAR")

    def _generate_POTCAR(self, potential):
        """
         generate POTCAR automatically, call the `cat` method of POTCAR
         """
        potcar = POTCAR.cat(potentials=potential, elements=self.elements, potdir=self.PotDir)
        self.valence = potcar.valence
        potcar.write(name="POTCAR")

    def _generate_submit(self, gamma=False, low=False, analysis=False):
        """
         generate job.submit automatically
         """
        content = SubmitFile(self.submit).strings
        self.finish = SubmitFile(self.submit).finish_line

        with open("submit.script", "w") as g:
            for line in content:
                if line.startswith("#SBATCH -J"):
                    g.write(f"#SBATCH -J {self.title} \n")
                else:
                    g.write(line)

        if gamma:
            with open("temp.sh", "w") as f:
                f.write("sed -i 's/vasp_std/vasp_gam/g' submit.script \n")
            os.system("bash temp.sh")
            os.remove("temp.sh")


class OutputTask(object):
    @staticmethod
    def output(name):
        """
        Transform the results to .xsd file
        """

        XSDFile.write(contcar="CONTCAR", outcar="OUTCAR", name=name)


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

    @end_symbol
    def generate(self, potential="PAW_PBE", continuous=False, low=False, print_end=True, vdw=False, sol=False,
                 gamma=False, nelect=None, mag=False):
        """
        rewrite BaseTask's generate
        """
        if continuous:
            self._generate_cdir()
        self._generate_POSCAR(continuous)
        self._generate_KPOINTS(gamma)
        self._generate_POTCAR(potential=potential)
        self._generate_INCAR(low=low, vdw=vdw, sol=sol, nelect=nelect, mag=mag)
        self._generate_submit(low=low, gamma=gamma)
        self._generate_info(potential=potential, gamma=gamma)
        if low and print_end:
            print(f"{RED}low first{RESET}")

    def _generate_cdir(self, dir="opt_cal", files=None):
        if files is None:
            files = ["INCAR", "CONTCAR"]
        super(OptTask, self)._generate_cdir(dir=dir, files=files)

    @write_wrapper
    def _generate_INCAR(self, low, vdw, sol, nelect, mag):
        """
        Inherit BaseTask's _generate_INCAR, but add wrapper to write INCAR
        """
        super(OptTask, self)._generate_INCAR(vdw, sol, nelect, mag)
        self.incar._ENCUT = self.incar.ENCUT
        if low:
            self.incar.ENCUT = 300.

    def _generate_submit(self, low=False, gamma=False, analysis=False):
        """
         generate job.submit automatically
         """
        super(OptTask, self)._generate_submit(low=low, analysis=analysis, gamma=gamma)

        run_command = SubmitFile(self.submit).run_line
        with open("submit.script", "a+") as g:
            if low:
                g.write("\n"
                        "#----------/Low Option/----------# \n"
                        "success=`grep accuracy OUTCAR | wc -l` \n"
                        "if [ $success -ne 1 ];then \n"
                        "  echo 'Optimization Task Failed!' \n"
                        "  exit 1 \n"
                        "fi \n"
                        "cp POSCAR POSCAR_300 \n"
                        "cp CONTCAR POSCAR \n"
                        "cp OUTCAR OUTCAR_300 \n"
                        "mv CONTCAR CONTCAR_300 \n"
                        f"sed -i 's/ENCUT = 300.0/ENCUT = {self.incar._ENCUT}/' INCAR\n"
                        f"\n"
                        f"{run_command}"
                        f"\n"
                        f"{self.finish}")

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

    @end_symbol
    def generate(self, potential="PAW_PBE", continuous=False, analysis=False, vdw=False, sol=False, gamma=False,
                 nelect=None):
        """
        rewrite BaseTask's generate
        """
        if continuous:
            self._generate_cdir()
        self._generate_POSCAR(continuous)
        self._generate_KPOINTS(gamma)
        self._generate_POTCAR(potential=potential)
        self._generate_INCAR(vdw=vdw, sol=sol, nelect=nelect)
        self._generate_submit(analysis=analysis, gamma=gamma)
        self._generate_info(potential=potential, gamma=gamma)

    def _generate_cdir(self, dir="chg_cal", files=None):
        if files is None:
            files = ["INCAR", "CONTCAR"]
        super(ChargeTask, self)._generate_cdir(dir=dir, files=files)

    @write_wrapper
    def _generate_INCAR(self, vdw, sol, nelect):
        """
        Inherit BaseTask's _generate_INCAR, modify parameters and write to INCAR
        parameters setting:
            IBRION = 1
            LAECHG = .TRUE.
            LCHARG = .TRUE.
        """
        super(ChargeTask, self)._generate_INCAR(vdw=vdw, sol=sol, nelect=nelect)
        self.incar.IBRION = 1
        self.incar.LAECHG = True
        self.incar.LCHARG = True

    def _generate_submit(self, analysis=False, gamma=False, low=False):
        """
         generate job.submit automatically
         """
        super(ChargeTask, self)._generate_submit(gamma=gamma)

        if analysis:
            ChargeTask.apply_analysis()

    @staticmethod
    def apply_analysis():
        with open("submit.script", "a+") as g:
            g.write("\n"
                    "#----------/Charge Analysis Option/----------#\n"
                    "success=`grep accuracy OUTCAR | wc -l` \n"
                    "if [ $success -ne 1 ];then \n"
                    "  echo 'Charge Task Failed!' \n"
                    "  exit 1 \n"
                    "fi \n"
                    "gvasp sum || chgsum.pl AECCAR0 AECCAR2 || return 1 \n"
                    "bader CHGCAR -ref CHGCAR_sum \n"
                    "\n"
                    "gvasp split || chgsplit.pl CHGCAR || return 1 \n"
                    "gvasp grd -d -1 || return 1 \n")

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


class WorkFuncTask(BaseTask):
    """
    Work Function calculation task manager, subclass of BaseTask
    """

    def generate(self, potential="PAW_PBE", continuous=False, vdw=False, sol=False, gamma=False, nelect=None,
                 mag=False):
        """
        fully inherit BaseTask's generate
        """
        super(WorkFuncTask, self).generate(potential=potential, continuous=continuous, vdw=vdw, sol=sol, gamma=gamma,
                                           nelect=nelect, mag=mag)

    def _generate_cdir(self, dir="workfunc", files=None):
        if files is None:
            files = ["INCAR", "CONTCAR"]
        super(WorkFuncTask, self)._generate_cdir(dir=dir, files=files)

    @write_wrapper
    def _generate_INCAR(self, vdw, sol, nelect):
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
        super(WorkFuncTask, self)._generate_INCAR(vdw, sol, nelect)
        self.incar.IBRION = -1
        self.incar.NSW = 1
        self.incar.LVHAR = True


class BandTask(BaseTask):
    """
    Band Structure calculation task manager, subclass of BaseTask
    """

    def generate(self, potential="PAW_PBE", continuous=False, vdw=False, sol=False, nelect=None, gamma=False,
                 mag=False):
        """
        fully inherit BaseTask's generate
        """
        super(BandTask, self).generate(potential=potential, continuous=continuous, vdw=vdw, sol=sol, nelect=nelect,
                                       mag=mag)

    def _generate_cdir(self, dir="band_cal", files=None):
        if files is None:
            files = ["INCAR", "CONTCAR", "CHGCAR"]
        super(BandTask, self)._generate_cdir(dir=dir, files=files)

    @write_wrapper
    def _generate_INCAR(self, vdw, sol, nelect):
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
        super(BandTask, self)._generate_INCAR(vdw, sol, nelect)
        self.incar.ISTART = 1
        self.incar.ICHARG = 11
        self.incar.IBRION = -1
        self.incar.NSW = 1
        self.incar.LCHARG = False

        if getattr(self.incar, "LAECHG", None) is not None:
            del self.incar.LAECHG

    def _generate_KPOINTS(self, gamma=False, points=21):
        """
        generate KPOINTS in line-mode
        """
        lattice = self.structure.lattice.matrix
        positions = self.structure.atoms.frac_coord
        numbers = self.structure.atoms.number
        spglib_structure = (lattice, positions, numbers)

        path = get_path(structure=spglib_structure)
        KLabel = path['point_coords']
        KPath = path['path']

        with open("KPOINTS", "w") as f:
            f.write("K Along High Symmetry Lines \n")
            f.write(f"{points} \n")
            f.write(f"Line-Mode \n")
            f.write(f"Rec \n")

            for (start, end) in KPath:
                start_str = [format(item, "8.5f") for item in KLabel[start]]
                end_str = [format(item, "8.5f") for item in KLabel[end]]

                f.write(f"{' '.join(start_str)}\t!{start} \n")
                f.write(f"{' '.join(end_str)}\t!{end} \n")
                f.write("\n")


class DOSTask(BaseTask):
    """
    Density of States (DOS) calculation task manager, subclass of BaseTask
    """

    def generate(self, potential="PAW_PBE", continuous=False, vdw=False, sol=False, gamma=False, nelect=None,
                 mag=False):
        """
        fully inherit BaseTask's generate
        """
        super(DOSTask, self).generate(potential=potential, continuous=continuous, vdw=vdw, sol=sol, gamma=gamma,
                                      nelect=nelect, mag=mag)

    def _generate_cdir(self, dir="dos_cal", files=None):
        if files is None:
            files = ["INCAR", "CONTCAR", "CHGCAR"]
        super(DOSTask, self)._generate_cdir(dir=dir, files=files)

    @write_wrapper
    def _generate_INCAR(self, vdw, sol, nelect):
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
        super(DOSTask, self)._generate_INCAR(vdw, sol, nelect)
        self.incar.ISTART = 1
        self.incar.ICHARG = 11
        self.incar.IBRION = -1
        self.incar.NSW = 1
        self.incar.LORBIT = 12
        self.incar.NEDOS = 2000
        self.incar.LCHARG = False

        if getattr(self.incar, "LAECHG", None) is not None:
            del self.incar.LAECHG


class FreqTask(BaseTask, Animatable):
    """
    Frequency calculation task manager, subclass of BaseTask
    """

    def generate(self, potential="PAW_PBE", continuous=False, vdw=False, sol=False, gamma=False, nelect=None,
                 mag=False):
        """
        fully inherit BaseTask's generate
        """
        super(FreqTask, self).generate(potential=potential, vdw=vdw, sol=sol, gamma=gamma, nelect=nelect, mag=mag)

    @write_wrapper
    def _generate_INCAR(self, vdw, sol, nelect):
        """
        Inherit BaseTask's _generate_INCAR, modify parameters and write to INCAR
        parameters setting:
            IBRION = 5
            ISYM = 0
            NSW = 1
            NFREE = 2
            POTIM = 0.015
        """
        super(FreqTask, self)._generate_INCAR(vdw=vdw, sol=sol, nelect=nelect)
        self.incar.IBRION = 5
        self.incar.ISYM = 0
        self.incar.NSW = 1
        self.incar.NFREE = 2
        self.incar.POTIM = 0.015

    @staticmethod
    def movie(file="OUTCAR", freq="image"):
        """
        visualize the frequency vibration, default: image
        """
        outcar = OUTCAR(file)
        outcar.animation_freq(freq=freq)


class MDTask(BaseTask, Animatable):
    """
     ab-initio molecular dynamics (AIMD) calculation task manager, subclass of BaseTask
     """

    def generate(self, potential="PAW_PBE", continuous=False, vdw=False, sol=False, gamma=False, nelect=None,
                 mag=False):
        """
        fully inherit BaseTask's generate
        """
        super(MDTask, self).generate(potential=potential, vdw=vdw, sol=sol, gamma=gamma, nelect=nelect, mag=mag)

    @write_wrapper
    def _generate_INCAR(self, vdw, sol, nelect):
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
        super(MDTask, self)._generate_INCAR(vdw=vdw, sol=sol, nelect=nelect)
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

    def generate(self, potential="PAW_PBE", continuous=False, vdw=False, sol=False, gamma=False, nelect=None,
                 mag=False):
        """
        fully inherit BaseTask's generate
        """
        super(STMTask, self).generate(potential=potential, vdw=vdw, sol=sol, gamma=gamma, nelect=nelect, mag=mag)

    @write_wrapper
    def _generate_INCAR(self, vdw, sol, nelect):
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
        super(STMTask, self)._generate_INCAR(vdw=vdw, sol=sol, nelect=nelect)
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

    def generate(self, potential="PAW_PBE", continuous=False, vdw=False, sol=False, gamma=False, nelect=None,
                 mag=False):
        """
        fully inherit BaseTask's generate
        """
        super(ConTSTask, self).generate(potential=potential, vdw=vdw, sol=sol, gamma=gamma, nelect=nelect, mag=mag)
        self._generate_fort()

    @write_wrapper
    def _generate_INCAR(self, vdw, sol, nelect):
        """
        Inherit BaseTask's _generate_INCAR, modify parameters and write to INCAR
        parameters setting:
            IBRION = 1
        """
        super(ConTSTask, self)._generate_INCAR(vdw=vdw, sol=sol, nelect=nelect)
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

    @end_symbol
    def generate(self, method="linear", check_overlap=True, potential="PAW_PBE", vdw=False, sol=False, gamma=False,
                 nelect=None):
        """
        Overwrite BaseTask's generate, add `method` and `check_overlap` parameters
        """
        self._generate_POSCAR(method=method, check_overlap=check_overlap)
        self._generate_KPOINTS(gamma)
        self._generate_POTCAR(potential=potential)
        self._generate_INCAR(vdw=vdw, sol=sol, nelect=nelect)
        self._generate_info(potential=potential, gamma=gamma)

    @write_wrapper
    def _generate_INCAR(self, vdw, sol, nelect):
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
        super(NEBTask, self)._generate_INCAR(vdw=vdw, sol=sol, nelect=nelect)
        self.incar.IBRION = 3
        self.incar.POTIM = 0.
        self.incar.SPRING = -5.
        self.incar.LCLIMB = False
        self.incar.ICHAIN = 0
        self.incar.IOPT = 3
        self.incar.MAXMOVE = 0.03
        self.incar.IMAGES = self.images

    def _generate_POSCAR(self, method=None, check_overlap=None, continuous=None):
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

        idpp_path = IdppPath.from_linear(self.ini_poscar, self.fni_poscar, self.images)
        idpp_path.run()
        idpp_path.write()

        logger.info("Improved interpolation of NEB initial guess has been generated.")

    def _generate_liner(self):
        """
        Generate NEB-task images by linear interpolation method
        """

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
    def generate(self, potential="PAW_PBE", continuous=False, vdw=False, sol=False, gamma=False, nelect=None, mag=False):
        """
        fully inherit BaseTask's generate
        """
        super(DimerTask, self).generate(potential=potential, vdw=vdw, sol=sol, gamma=gamma, nelect=nelect, mag=mag)

    @write_wrapper
    def _generate_INCAR(self, vdw, sol, nelect):
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
        super(DimerTask, self)._generate_INCAR(vdw=vdw, sol=sol, nelect=nelect)
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


class SequentialTask(object):
    """
    Apply Sequential Task from `opt => chg` or `opt => dos`
    """

    def __init__(self, end):
        """
        Args:
            end: specify the end task, optional: [opt, chg, dos]
        """
        self.end = end

    @end_symbol
    def generate(self, potential="PAW_PBE", low=False, analysis=False, vdw=False, sol=False, gamma=False, nelect=None):
        task = OptTask()
        task.generate(potential=potential, low=low, print_end=False, vdw=vdw, sol=sol, gamma=gamma, nelect=nelect)

        run_command = SubmitFile("submit.script").run_line
        finish_command = SubmitFile("submit.script").finish_line

        if self.end == "chg" or self.end == "dos":
            low_string = "low first, " if low else ""
            analysis_string = "apply analysis" if analysis else ""
            print(f"{RED}Sequential Task: opt => {self.end}, " + low_string + analysis_string + RESET)
            with open("submit.script", "a+") as g:
                g.write("\n"
                        "#----------/Charge Option/----------# \n"
                        "success=`grep accuracy OUTCAR | wc -l` \n"
                        "if [ $success -ne 1 ];then \n"
                        "  echo 'Optimization Task Failed!' \n"
                        "  exit 1 \n"
                        "fi \n"
                        "mkdir chg_cal \n"
                        "cp OUTCAR OUTCAR_backup \n"
                        "cp INCAR KPOINTS POTCAR chg_cal \n"
                        "cp CONTCAR chg_cal/POSCAR \n"
                        f"sed -i '/IBRION/c\  IBRION = 1' chg_cal/INCAR \n"
                        f"sed -i '/LCHARG/c\  LCHARG = .TRUE.' chg_cal/INCAR \n"
                        f"sed -i '/LCHARG/a\  LAECHG = .TRUE.' chg_cal/INCAR \n"
                        f"cd chg_cal || return \n"
                        f"\n"
                        f"{run_command}"
                        f"\n"
                        f"{finish_command}")
            if analysis:
                ChargeTask.apply_analysis()

        if self.end == "wf":
            low_string = "low first, " if low else ""
            print(f"{RED}Sequential Task: opt => {self.end}, " + low_string + RESET)
            with open("submit.script", "a+") as g:
                g.write("\n"
                        "#----------/WorkFunc Option/----------# \n"
                        "success=`grep accuracy OUTCAR | wc -l` \n"
                        "if [ $success -ne 1 ];then \n"
                        "  echo 'Optimization Task Failed!' \n"
                        "  exit 1 \n"
                        "fi \n"
                        "mkdir workfunc \n"
                        "cp OUTCAR OUTCAR_backup \n"
                        "cp INCAR KPOINTS POTCAR workfunc \n"
                        "cp CONTCAR workfunc/POSCAR \n"
                        f"sed -i '/IBRION/c\  IBRION = -1' workfunc/INCAR \n"
                        f"sed -i '/NSW/c\  NSW = 1' workfunc/INCAR \n"
                        f"sed -i '/NSW/a\  LVHAR = .TRUE.' workfunc/INCAR \n"
                        f"cd workfunc || return \n"
                        f"\n"
                        f"{run_command}"
                        f"\n"
                        f"{finish_command}")

        if self.end == "dos":
            with open("submit.script", "a+") as g:
                g.write("\n"
                        "#----------/DOS Option/----------# \n"
                        "success=`grep accuracy OUTCAR | wc -l` \n"
                        "if [ $success -ne 1 ];then \n"
                        "  echo 'Charge Task Failed!' \n"
                        "  exit 1 \n"
                        "fi \n"
                        "mkdir dos_cal \n"
                        "cp OUTCAR OUTCAR_backup \n"
                        "cp INCAR KPOINTS POTCAR CHGCAR dos_cal \n"
                        "cp CONTCAR dos_cal/POSCAR \n"
                        f"sed -i '/ISTART/c\  ISTART = 1' dos_cal/INCAR \n"
                        f"sed -i '/NSW/c\  NSW = 1' dos_cal/INCAR \n"
                        f"sed -i '/IBRION/c\  IBRION = -1' dos_cal/INCAR \n"
                        f"sed -i '/LCHARG/c\  LCHARG = .FALSE.' dos_cal/INCAR \n"
                        f"sed -i '/LCHARG/a\  LAECHG = .FALSE.' dos_cal/INCAR \n"
                        f"sed -i '/+U/i\  ICHARG = 11' dos_cal/INCAR \n"
                        f"sed -i '/ICHARG/a\  LORBIT = 12' dos_cal/INCAR \n"
                        f"sed -i '/ICHARG/a\  NEDOS = 2000' dos_cal/INCAR \n"
                        f"cd dos_cal || return \n"
                        f"\n"
                        f"{run_command}"
                        f"\n"
                        f"{finish_command}")

        if self.end not in ['opt', 'chg', 'wf', 'dos']:
            raise TypeError(f"Unsupported Sequential Task to {self.end}, should be [opt, chg, wf, dos]")

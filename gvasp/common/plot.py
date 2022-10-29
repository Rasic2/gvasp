import logging
import time
from collections import defaultdict
from functools import wraps
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandas import DataFrame
from scipy import interpolate
from scipy.integrate import simps

from gvasp.common.figure import Figure, SolidLine, DashLine, Text, plot_wrapper, PchipLine
from gvasp.common.file import CONTCAR, DOSCAR, EIGENVAL, OUTCAR, POSCAR, LOCPOT
from gvasp.common.structure import Structure
from gvasp.common.task import NEBTask

pd.set_option('display.max_columns', None)  # show all columns
pd.set_option('display.max_rows', None)  # show all rows

COLUMNS = ['s_up', 's_down', 'py_up', 'py_down', 'pz_up', 'pz_down', 'px_up', 'px_down', 'dxy_up', 'dxy_down',
           'dyz_up', 'dyz_down', 'dz2_up', 'dz2_down', 'dxz_up', 'dxz_down', 'dx2_up', 'dx2_down', 'f1_up',
           'f1_down', 'f2_up', 'f2_down', 'f3_up', 'f3_down', 'f4_up', 'f4_down', 'f5_up', 'f5_down', 'f6_up',
           'f6_down', 'f7_up', 'f7_down']

logger = logging.getLogger(__name__)


def interpolated_wrapper(func):
    @wraps(func)
    def wrapper(self):
        x_out, y_out = [], []
        for x, y, number in func(self):
            x_arr = np.array(x)
            y_arr = np.array(y)
            x_new = np.linspace(np.min(x_arr), np.max(x_arr), len(x) * 100)
            f = interpolate.interp1d(x_arr, y_arr, kind='cubic')
            y_new = f(x_new)

            if not self.avgflag:
                number = 1

            if self.method == 'fill':
                plt.fill(x_new, y_new / number, color=self.color, alpha=self.alpha)
            elif self.method == 'line':
                plt.plot(x_new, y_new / number, color=self.color)
            elif self.method == 'dash line':
                plt.plot(x_new, y_new / number, '--', color=self.color)
            elif self.method == 'output':
                x_out.append(x_new)
                y_out.append(y_new)

        if self.method == 'output':
            x_out = np.array(x_out).transpose((1, 0))  # construct np.array and transpose the (0, 1) axis for plot after
            y_out = np.array(y_out).transpose((1, 0))
            time_prefix = time.strftime("%H-%M-%S", time.localtime())
            np.savetxt(f"datafile_x_{time_prefix}", x_out)
            np.savetxt(f"datafile_y_{time_prefix}", y_out)

    return wrapper


class PlotDOS(Figure):
    """
    <PlotDOS main class>

    @method:
        plot():     plot main func
        center():   calculate the band-center

    @static-method:
        contcar_parse:  parse CONTCAR data
        doscar_parse:   parse DOSCAR data
    """

    def __init__(self, dos_file, pos_file, xlabel="Energy (eV)", ylabel="Density of States (a.u.)", **kargs):
        super(PlotDOS, self).__init__(xlabel=xlabel, ylabel=ylabel, **kargs)
        self.dos_file = dos_file
        self.pos_file = pos_file
        self.element = PlotDOS.parse_contcar(self.pos_file)
        self.total_dos, self.atom_list = PlotDOS.parse_doscar(self.dos_file)

        self.atoms, self.orbitals, self.color, self.method, self.avgflag = None, None, None, None, None

    @plot_wrapper
    def plot(self, atoms=None, orbitals=None, color="#000000", method='line', avgflag=False, alpha=0.5):
        """
        Plot DOS Main Func

        @params:
            atoms:      accept int, list, and str('1-10' or 'Ce') type
            orbitals:   list, e.g., ['s',  'p']
            method:     ['line', 'dash line','fill', 'output']
            avgflag:    whether calculate the average dos
        """

        self.atoms = atoms
        self.orbitals = orbitals
        self.color = color  # this argument will transfer to interpolated_wrapper
        self.alpha = alpha  # this argument will transfer to interpolated_wrapper (fill only)
        self.method = method
        self.avgflag = avgflag

        @interpolated_wrapper
        def plot_tot(self):
            """Plot Total DOS"""
            for column in self.total_dos.columns.values:
                yield self.total_dos.index.values, list(self.total_dos[column].values), 1

        @interpolated_wrapper
        def plot_atoms(self):
            """Plot DOS of atom list"""
            plus_tot = defaultdict(list)
            plus_tot = DataFrame(plus_tot, index=self.atom_list[0],
                                 columns=['up', 'down', 'p_up', 'p_down', 'd_up', 'd_down', 'f_up', 'f_down'] + COLUMNS,
                                 dtype='object')
            plus_tot.iloc[:, :] = 0.0
            for atom in self.atoms:
                for column in plus_tot.columns.values:
                    try:
                        plus_tot[column] += self.atom_list[atom][column]
                    except KeyError:
                        plus_tot[column] = 0

            if self.orbitals is None:
                orbitals = [plus_tot['up'].values, plus_tot['down'].values]
            else:
                orbitals = [plus_tot[item[0] + item[1]] for item in product(self.orbitals, ['_up', '_down'])]

            for orbital_value in orbitals:
                yield plus_tot.index.values, orbital_value, len(self.atoms)

        def identify_atoms(self):
            """Calculate the real index for the atoms"""
            if not isinstance(self.atoms, list):
                self.atoms = [self.atoms]

            inner_atoms = []
            for item in self.atoms:
                if isinstance(item, int):
                    inner_atoms.append(item)
                elif isinstance(item, str):
                    if '-' in item:
                        slice_atoms = [int(item) for item in item.split('-')]
                        if slice_atoms[1] >= len(self.element):
                            logger.error(f"The end index `{slice_atoms[1]}` > atoms count ({len(self.element) - 1})")
                            exit(1)
                        inner_atoms += list(range(slice_atoms[0], slice_atoms[1] + 1, 1))
                    else:
                        element_atoms = [index for index, element in enumerate(self.element) if item == element]
                        if len(element_atoms) == 0:
                            logger.warning(f"Atoms don't have <Element {item}>, ignore it!")
                        inner_atoms += element_atoms
                else:
                    raise TypeError(f"The format of {self.atoms} is not correct!")

            set_atoms = set(inner_atoms)
            if len(inner_atoms) != len(set_atoms):
                logger.warning("The specification of atoms have repeat items, we will only plot once for it!")

            self.atoms = list(set_atoms)

        """Main Content of Plot func"""
        if self.atoms is None:
            return plot_tot(self)
        elif isinstance(self.atoms, (list, int, str)):
            identify_atoms(self)
            return plot_atoms(self)
        else:
            raise ValueError(f"The format of {self.atoms} is not correct!")

    def center(self, atoms=None, orbitals=None, xlim=None):
        """
        Calculate Band-Center Value (can't put in the <DOSCAR class>, causing it needs CONTCAR information)
        """

        old_atoms = atoms
        if isinstance(old_atoms, str):
            if '-' in old_atoms:
                pre_atom = [int(item) for item in old_atoms.split('-')]
                atoms = list(range(pre_atom[0], pre_atom[1] + 1, 1))
            else:
                atoms = [index for index, element in enumerate(self.element) if old_atoms == element]

        y = 0
        rang = (self.total_dos.index.values < xlim[1]) & (self.total_dos.index.values > xlim[0])
        if atoms is None:
            y += self.total_dos.loc[rang, 'tot_up']
            y -= self.total_dos.loc[rang, 'tot_down']
        elif orbitals is not None:
            for atom in atoms:
                for orbital in orbitals:
                    y += self.atom_list[atom].loc[rang, f'{orbital}_up']
                    y -= self.atom_list[atom].loc[rang, f'{orbital}_down']
        else:
            for atom in atoms:
                y += self.atom_list[atom].loc[rang, 'up']
                y -= self.atom_list[atom].loc[rang, 'down']
        e_count = simps(y.values, y.index.values)  # Simpson Integration method for obtain the electrons' num
        dos = simps([a * b for a, b in zip(y.values, y.index.values)], y.index.values)
        print(f"Number of Electrons: {e_count:.4f}; Center Value: {dos / e_count:.4f}")

    @staticmethod
    def parse_contcar(name):
        """
        read CONTCAR file, obtain the elements' list.

        @params:
            name:       CONTCAR file name

        @return:
            element:    elements list, e.g., ['','Be','Be','C']
        """

        structure = CONTCAR(name=name).structure
        element = [' '] + structure.atoms.formula
        return element

    @staticmethod
    def parse_doscar(name):
        """
        read DOSCAR file, obtain the TDOS && LDOS.

        @params:
            name:       DOSCAR file name

        @return:
            TDOS:       DataFrame(NDOS, 2)
            LDOS:       energy_list + List(NAtom * DataFrame(NDOS, NOrbital+8))
        """
        dos_instance = DOSCAR(name=name).load()
        return dos_instance.TDOS, dos_instance.LDOS


class PlotOpt(Figure):
    def __init__(self, name="OUTCAR", width=16, title="Structure Optimization", xlabel="Steps", **kargs):
        super(PlotOpt, self).__init__(width=width, title=title, xlabel=xlabel, **kargs)
        self.name = name
        outcar = OUTCAR(name=self.name)
        self.energy = outcar.energy
        self.force = outcar.force

    def plot(self, color=("#ed0345", "#009734")):
        self._plot_energy(color=color[0])
        self._plot_force(color=color[1])

    @plot_wrapper
    def _plot_energy(self, color):
        plt.subplot(121)
        plt.plot(self.energy, "-o", color=color)

    @plot_wrapper
    def _plot_force(self, color):
        plt.subplot(122)
        plt.plot(self.force, "-o", color=color)


class PlotBand(Figure):
    def __init__(self, name="EIGENVAL", title='Band Structure', **kargs):
        super(PlotBand, self).__init__(title=title, **kargs)
        self.name = name
        if self.name.startswith("EIGENVAL"):
            self.energy = EIGENVAL(self.name).energy
        elif self.name.startswith("OUTCAR"):
            energy = OUTCAR(self.name).band_info
            self.energy = np.concatenate((energy.up[:, :, np.newaxis], energy.down[:, :, np.newaxis]), axis=2)
            self.energy = self.energy.transpose((1, 0, 2))

        try:
            self.fermi = OUTCAR("OUTCAR").fermi
        except FileNotFoundError:
            logger.warning("`OUTCAR` not found, set E-fermi=0.0")
            self.fermi = 0.

    @plot_wrapper
    def plot(self):
        """
        Plot Band Structure, for spin-system, the average energy was applied
        """
        energy_avg = self.energy.mean(axis=-1) - self.fermi
        for band_index in range(energy_avg.shape[1]):
            plt.plot(energy_avg[:, band_index], "-o")


class PlotEPotential(Figure):
    def __init__(self, direction='z', title='Local Potential', xlabel='Position (Å)', ylabel='Energy (eV)', **kargs):
        super(PlotEPotential, self).__init__(title=title, xlabel=xlabel, ylabel=ylabel, **kargs)
        self.lpotential = LOCPOT(name="LOCPOT").line_potential(direction=direction)

    @plot_wrapper
    def plot(self):
        """
        Plot Electrostatic Potential
        """
        plt.plot(*self.lpotential)


class PESData(object):
    """
    Generate the data for PlotPES

    @method:
        convert_sd:    func for converting data to solid_dash type
        convert_sc:    func for converting data to solid_curve type
    """

    def __init__(self, data):
        self.data = data

    def __call__(self, style="solid_dash"):
        if style == "solid_dash":
            self.solid_x, self.solid_y, self.dash_x, self.dash_y = self.convert_sd()
        elif style == "solid_curve":
            self.solid_x_1, self.solid_y_1, self.solid_x_2, self.solid_y_2, self.pchip_x, self.pchip_y = self.convert_sc()
        return self

    def convert_sd(self):
        """
        func for converting data to solid_dash type

        @return:
            solid_x: x position in bi-tuple format of solid-type line (MS/TS-state)
            solid_y: y position in bi-tuple format of solid-type line (MS/TS-state)
            dash_x: x position in bi-tuple format of dash-type line (MS/TS)-(MS/TS)
            dash_y: y position in bi-tuple format of dash-type line (MS/TS)-(MS-TS)
        """
        solid_x = [[0.75 + 2 * i, 1.25 + 2 * i] for i in range(len(self.data))]
        solid_y = [[value, value] for value in self.data]
        real_index = [index for index, value in enumerate(self.data) if value is not None]
        dash_x_1 = [2 * index + 1.25 for index in real_index[:-1]]
        dash_x_2 = [2 * index + 0.75 for index in real_index[1:]]
        dash_x = [item for item in zip(dash_x_1, dash_x_2)]
        dash_y = [[self.data[int((index[0] - 1.25) / 2)], self.data[int((index[1] - 2.75) / 2 + 1)]] for index in
                  dash_x]
        return solid_x, solid_y, dash_x, dash_y

    def convert_sc(self):
        """
        func for converting data to solid_curve type

        @return:
            solid_x_1: x position in bi-tuple format of solid-type line (MS state)
            solid_y_1: y position in bi-tuple format of solid-type line (MS state)
            solid_x_2: y position in bi-tuple format of solid-type line (MS-MS)
            solid_y_2: y position in bi-tuple format of solid-type line (MS-MS)
            pchip_x: x position in tri-tuple format of pchip-type line (MS-TS-MS)
            pchip_y: y position in tri-tuple format of pchip-type line (MS-TS-MS)
        """
        energies, labels = self.data
        solid_x_1 = [[0.75 + 2 * i, 1.25 + 2 * i] for i, label in enumerate(labels) if label != "TS"]
        solid_y_1 = [[energy, energy] for energy, label in zip(energies, labels) if label != "TS"]

        solid_i_2 = [i for i, item in enumerate(energies) if item is not None]  # locate non-None index
        solid_i_2 = [[i1, i2] for i1, i2 in zip(solid_i_2[:-1], solid_i_2[1:]) if
                     labels[i1] != "TS" and labels[i2] != "TS"]
        solid_x_2 = [[1.25 + 2 * i1, 0.75 + 2 * i2] for i1, i2 in solid_i_2]
        solid_y_2 = [[energies[i1], energies[i2]] for i1, i2 in solid_i_2]

        pchip_i = [i for i, item in enumerate(energies) if item is not None]  # locate non-None index
        pchip_i = [[i1, i2, i3] for i1, i2, i3 in zip(pchip_i[:-2], pchip_i[1:-1], pchip_i[2:]) if
                   labels[i1] == "MS" and labels[i2] == "TS" and labels[i3] == "MS"]
        pchip_x = [[1.25 + 2 * i1, 1 + 2 * i2, 0.75 + 2 * i3] for i1, i2, i3 in pchip_i]
        pchip_y = [[energies[i1], energies[i2], energies[i3]] for i1, i2, i3 in pchip_i]
        return solid_x_1, solid_y_1, solid_x_2, solid_y_2, pchip_x, pchip_y


class PlotPES(Figure):
    """
    Plot potential energy surface (PES)

    @method:
        plot():     plot main func

        add_solid:  auxiliary func, add solid line
        add_dash:   auxiliary func, add dash line
        add_text:   auxiliary func, add text
    """

    def __init__(self, width=15.6, height=4, weight='bold', xlabel="Reaction coordinates", ylabel="Energy (eV)",
                 xticks=[], bwidth=3, **kargs):
        super(PlotPES, self).__init__(width=width, height=height, weight=weight, xlabel=xlabel, ylabel=ylabel,
                                      xticks=xticks, bwidth=bwidth, **kargs)

        self.texts = defaultdict(list)

    @staticmethod
    def add_solid(linewidth, x, y, color):
        SolidLine(linewidth, x=x, y=y, color=color)()

    @staticmethod
    def add_dash(linewidth, x, y, color):
        DashLine(linewidth, x=x, y=y, color=color)()

    @staticmethod
    def add_pchip(linewidth, x, y, color, num=100):
        PchipLine(linewidth, num=num, x=x, y=y, color=color)()

    def add_text(self, x, y, text, color):
        self.texts[color].append(Text(self, x, y, text, color))

    @plot_wrapper
    def plot(self, data, color, text_flag=True, style="solid_dash"):
        """
        Main plot func of <PlotPES class>

        @param:
            data:       energy or (energy, label) types data
            color:      specify which color you want to plot
            text_flag:  only affect `solid_dash` type
            style:      specify which style PES you want to plot, default: solid_dash
        """
        data = PESData(data)(style=style)

        if style == "solid_dash":
            self._plot_solid_dash(data, color, text_flag=text_flag)
        elif style == "solid_curve":
            self._plot_solid_curve(data, color)
        else:
            raise NotImplementedError("style should be `solid_dash` or `solid_curve`")

    def _plot_solid_dash(self, data, color, text_flag):
        for x, y in zip(data.solid_x, data.solid_y):
            self.add_solid(5, x, y, color)

        for x, y in zip(data.dash_x, data.dash_y):
            self.add_dash(1.5, x, y, color)
            self.add_text(x, y, '{:.2f}'.format(abs(y[1] - y[0])), color) if text_flag else 0

    def _plot_solid_curve(self, data, color):
        for x, y in zip(data.solid_x_1, data.solid_y_1):
            self.add_solid(3, x, y, color)

        for x, y in zip(data.solid_x_2, data.solid_y_2):
            self.add_solid(1, x, y, color)

        for x, y in zip(data.pchip_x, data.pchip_y):
            self.add_pchip(2, x, y, color)


class PlotNEB(Figure):

    def __init__(self, xlabel="Distance (Å)", ylabel="Energy (eV)", width=10, **kargs):
        super(PlotNEB, self).__init__(xlabel=xlabel, ylabel=ylabel, width=width, **kargs)

    @plot_wrapper
    def plot(self, color="#ed0345", workdir=None):
        neb_dirs = NEBTask._search_neb_dir(workdir)
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

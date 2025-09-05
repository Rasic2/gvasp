import logging
from collections import defaultdict, namedtuple
from functools import wraps
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandas import DataFrame
from scipy import interpolate
from scipy.integrate import simps

from gvasp.common.constant import COLUMNS_32
from gvasp.common.figure import Figure, SolidLine, DashLine, Text, plot_wrapper, PchipLine
from gvasp.common.file import CONTCAR, DOSCAR, EIGENVAL, OUTCAR, POSCAR, LOCPOT, CHGCAR_diff, KPATHIN
from gvasp.common.structure import Structure
from gvasp.common.task import NEBTask
from gvasp.common.utils import identify_atoms, search_peak

pd.set_option('display.max_columns', None)  # show all columns
pd.set_option('display.max_rows', None)  # show all rows

logger = logging.getLogger(__name__)


def interpolated_wrapper(func):
    @wraps(func)
    def wrapper(self):
        DOSL_data = namedtuple("DOSL_data", ("energy", "up", "down"))
        x_out, y_out = [], []
        for x, y, number, magnification in func(self):
            x_arr = np.array(x)
            y_arr = np.array(y)
            x_new = np.linspace(np.min(x_arr), np.max(x_arr), len(x) * magnification)
            f = interpolate.interp1d(x_arr, y_arr, kind='cubic')
            y_new = f(x_new)

            if not self.avgflag:
                number = 1

            x_out.append(x_new)
            y_out.append(y_new / number)

        DOSL_data.energy = x_out[0]
        DOSL_data.up = y_out[0]
        DOSL_data.down = y_out[1]

        return DOSL_data

    return wrapper


class PostDOS(Figure):

    def __init__(self, dos_files: list, pos_files: list, ISPIN=2, LORBIT=12, align=None, xlabel="Energy (eV)",
                 ylabel="Density of States (a.u.)", **kargs):
        super(PostDOS, self).__init__(xlabel=xlabel, ylabel=ylabel, **kargs)

        self.managers = [DOSData(dos_file=dos_file, pos_file=pos_file, ISPIN=ISPIN, LORBIT=LORBIT) for
                         dos_file, pos_file in zip(dos_files, pos_files)]

        self.align = align

    @plot_wrapper
    def plot(self, selector: dict):
        """
        <Plot DOS Method>

        Args:
            selector (dict): keys: [atoms, orbitals, color, method, alpha]
            selector.method (optional): ["line", "dash line", "fill", "output"]

            Examples
            ---------
            >>> selector

            selector = {"0": [{"atoms": "C", "orbitals": ["p"], "color": "#ed0345", "method": "fill", "alpha": 0.3},
                              {"atoms": "1-10", "orbitals": ["s", "d"], "color": "#098760"}],
                        "1": [{"atoms": [0, 1, "H"], "orbitals": ["p"], "color": "#ed0345"},
                              {"atoms": 12, "orbitals": ["s", "p"], "color": "#098760"}]}

        Returns:
            display or save the DOS figures
        """
        DOSdata = defaultdict(list)

        for key in selector.keys():
            for line_argument in selector[key]:
                DOSdata[key].append(self.managers[int(key)].get_data(**line_argument))

        # Align the DOS
        if self.align is not None:
            if len(self.align) == len(self.managers):
                logger.info(" +" + "-".center(80, "-") + "+")
                logger.info(" |" + f"Align DOS relative to the first system".center(80, " ") + "|")
                logger.info(" |" + "-".center(80, "-") + "|")
                for index, item in enumerate(self.align):
                    if len(item) == 2:
                        if index == 0:
                            reference = self.managers[index].atom_list[item[0] + 1][item[1] + '_up']
                            refer_extremes = search_peak(reference)
                        current = self.managers[index].atom_list[item[0] + 1][item[1] + '_up']
                        current_extremes = search_peak(current)
                        diff_extreme = current_extremes[0] - refer_extremes[0]
                        for dos_line in DOSdata[str(index)]:
                            dos_line.energy -= diff_extreme
                        logger.info("|" + f" Align {index + 1}".center(10) + "|"
                                    + f"atom: {item[0]} orbital: {item[1]}".center(24) + "|"
                                    + f"ε_ref: {current_extremes[0]:.4f} eV".center(22)
                                    + f"Δε: {diff_extreme:+.4f} eV".center(22) + "|")
                    else:
                        raise TypeError(f"<align> should specify the atom and orbital at the same time, e.g. (10, 's')")

                logger.info("|" + "-".center(80, "-") + "|")
            else:
                logger.warning(f"The number of `align` is not equal to that of the files, ignore it.")

        for key in selector.keys():
            for index, line_argument in enumerate(selector[key]):
                method = line_argument.get("method", "line")
                label = line_argument.get("label", None)
                DOSL_data = DOSdata[key][index]
                if method == 'line':
                    plt.plot(DOSL_data.energy, DOSL_data.up, color=line_argument.get("color"), label=label)
                    plt.plot(DOSL_data.energy, DOSL_data.down, color=line_argument.get("color"))
                elif method == 'dash line':
                    plt.plot(DOSL_data.energy, DOSL_data.up, '--', color=line_argument.get("color"))
                    plt.plot(DOSL_data.energy, DOSL_data.down, '--', color=line_argument.get("color"))
                elif method == 'fill':
                    plt.fill_between(DOSL_data.energy, DOSL_data.up, DOSL_data.down, color=line_argument.get("color"),
                                     alpha=line_argument.get("alpha", 1.))
                elif method == 'output':
                    DOSL_ndata = np.array([DOSL_data.energy, DOSL_data.up, DOSL_data.down]).transpose((1, 0))
                    np.savetxt(f"DOS_F{key}_L{index}", DOSL_ndata, fmt='%.6e', delimiter="\t",
                               header="energy, up, down")

    def center(self, selector: dict):
        """Calculate Band-Center Value"""

        manager = self.managers[0]
        elements = manager.elements
        total_dos = manager.total_dos
        atom_list = manager.atom_list

        atoms = identify_atoms(selector.get("atoms", None), elements)
        orbitals = selector.get("orbitals", None)
        xlim = selector["xlim"]

        y = 0
        rang = (total_dos.index.values < xlim[1]) & (total_dos.index.values > xlim[0])
        if len(atoms) == len(elements) - 1 and orbitals is None:
            orbitals = "All"
            y += total_dos.loc[rang, 'tot_up']
            y -= total_dos.loc[rang, 'tot_down']
        elif orbitals is None:
            orbitals = "All"
            for atom in atoms:
                y += atom_list[atom].loc[rang, 'up']
                y -= atom_list[atom].loc[rang, 'down']
        else:
            for atom in atoms:
                for orbital in orbitals:
                    y += atom_list[atom].loc[rang, f'{orbital}_up']
                    y -= atom_list[atom].loc[rang, f'{orbital}_down']

        e_count = simps(y.values, y.index.values)  # Simpson Integration method for obtain the electrons' num
        dos = simps([a * b for a, b in zip(y.values, y.index.values)], y.index.values)

        # format atoms output
        format_atoms = ""
        loop_atoms = ""
        for index, atom in enumerate(atoms):
            loop_atoms += f"{atom} "
            if len(loop_atoms) == 36 or index == len(atoms) - 1:
                loop_atoms = loop_atoms.ljust(38) + "|"
                loop_atoms += "\n"
                format_atoms += loop_atoms
                if index != len(atoms) - 1:
                    format_atoms += "| ".ljust(18)
                else:
                    format_atoms += "| ".ljust(56) + "|"
                loop_atoms = ""

        print("+" + "-".center(55, "-") + "+")
        print("|" + f"Band-Center Calculation".center(55, " ") + "|")
        print("|" + "-".center(55, "-") + "|")
        print(f"| Selected Atoms: {format_atoms}")
        print(f"| Selected Orbitals: {orbitals}".ljust(56, ) + "|")
        print(f"| Energy Range: {xlim}".ljust(56, ) + "|")
        print(f"| Number of Electrons: {e_count:.4f}".ljust(56, ) + "|")
        print(f"| Center Value: {dos / e_count:.4f}".ljust(56, ) + "|")
        print("+" + "-".center(55, "-") + "+")


class DOSData():
    """
    <DOSData main class>

    Methods:
        get_data():     get_data main func
        center():   calculate the band-center

        contcar_parse:  parse CONTCAR data
        doscar_parse:   parse DOSCAR data
    """

    def __init__(self, dos_file, pos_file, ISPIN=2, LORBIT=12, magnification=100):
        self.dos_file = dos_file
        self.pos_file = pos_file
        self.elements = DOSData.parse_contcar(self.pos_file)
        self.total_dos, self.atom_list = DOSData.parse_doscar(self.dos_file, ISPIN, LORBIT)
        self.magnification = magnification

        self.atoms, self.orbitals, self.method, self.avgflag = None, None, None, None

    def get_data(self, atoms=None, exclude=None, orbitals=None, avgflag=False, **kargs):
        """
        <Get_Data Main Func>

        Args:
            atoms:      accept int, list, and str('1-10' or 'Ce') type
            exclude:    remove specified atoms in <atoms parameters>
            orbitals:   list, e.g., ['s',  'p']
            avgflag (bool):    whether calculate the average dos
        """

        self.atoms = atoms
        self.exclude = exclude
        self.orbitals = orbitals
        self.avgflag = avgflag

        @interpolated_wrapper
        def TDOS_data(self):
            """Get Total DOS"""
            for column in self.total_dos.columns.values:
                yield self.total_dos.index.values, list(self.total_dos[column].values), 1, self.magnification

        @interpolated_wrapper
        def LDOS_data(self):
            """Get DOS of atom list"""
            plus_tot = defaultdict(list)
            plus_tot = DataFrame(plus_tot, index=self.atom_list[0],
                                 columns=['up', 'down', 'p_up', 'p_down', 'd_up', 'd_down', 'f_up', 'f_down'] +
                                         COLUMNS_32, dtype='object')
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
                orbitals_up = np.array([plus_tot[item[0] + item[1]] for item in product(self.orbitals, ['_up'])])
                orbitals_down = np.array([plus_tot[item[0] + item[1]] for item in product(self.orbitals, ['_down'])])
                orbitals = [np.sum(orbitals_up, axis=0), np.sum(orbitals_down, axis=0)]

            for orbital_value in orbitals:
                yield plus_tot.index.values, orbital_value, len(self.atoms), self.magnification

        """Main Content of get_data func"""
        if self.atoms is None:
            return TDOS_data(self)
        elif isinstance(self.atoms, (list, int, str)):
            self.atoms = identify_atoms(self.atoms, self.elements)
            if self.exclude is not None:
                self.exclude = identify_atoms(self.exclude, self.elements)
                self.atoms = list(set(self.atoms) - set(self.exclude))
            return LDOS_data(self)
        else:
            raise ValueError(f"The format of {self.atoms} is not correct!")

    @staticmethod
    def parse_contcar(name):
        """
        read CONTCAR file, obtain the elements' list.

        Args:
            name:       CONTCAR file name

        Returns:
            element:    elements list, e.g., ['','Be','Be','C']
        """

        structure = CONTCAR(name=name).structure
        elements = [' '] + structure.atoms.formula
        return elements

    @staticmethod
    def parse_doscar(name, ISPIN, LORBIT):
        """
        read DOSCAR file, obtain the TDOS && LDOS.

        Args:
            name:       DOSCAR file name

        Returns:
            TDOS:       DataFrame(NDOS, 2)
            LDOS:       energy_list + List(NAtom * DataFrame(NDOS, NOrbital+8))
        """
        dos_instance = DOSCAR(name=name, ISPIN=ISPIN, LORBIT=LORBIT).load()
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
    def __init__(self, name="EIGENVAL", type="EIGENVAL", title='Band Structure', **kwargs):
        self.name = name
        self.type = type
        if self.type == "EIGENVAL":
            eigenval = EIGENVAL(self.name)
            self.energy, self.kcoord, self.klabel = eigenval.energy, eigenval.KPoint_dist, eigenval.KPoint_label
            self.pticks, self.plabel = list(
                map(list, zip(*[(self.kcoord[index], self.klabel[index]) for index, label in enumerate(self.klabel) if
                                len(label)])))
        elif self.type == "OUTCAR":
            energy = OUTCAR(self.name).band_info
            self.energy = np.concatenate((energy.up[:, :, np.newaxis], energy.down[:, :, np.newaxis]), axis=2)
            self.energy = self.energy.transpose((1, 0, 2))

        super(PlotBand, self).__init__(title=title, xlim=[self.kcoord[0], self.kcoord[-1]], **kwargs)

        try:
            self.fermi = OUTCAR("OUTCAR").fermi
        except FileNotFoundError:
            logger.warning("`OUTCAR` not found, set E-fermi=0.0")
            self.fermi = 0.

    @plot_wrapper(type="PlotBand")
    def plot(self):
        """
        Plot Band Structure, for spin-system, the average energy was applied
        """
        energy_avg = self.energy.mean(axis=-1) - self.fermi
        for band_index in range(energy_avg.shape[1]):
            plt.plot(self.kcoord, energy_avg[:, band_index], "-o")

        for line in self.pticks:
            if line == 0. or line == self.kcoord[-1]:
                continue
            plt.vlines(line, ymin=self.ylim[0], ymax=self.ylim[1], linestyles="dashed", linewidth=2)

        plt.xticks(ticks=self.pticks, labels=self.plabel, fontsize=self.fontsize)


class PlotEPotential(Figure):
    def __init__(self, direction='z', output=True, title='Local Potential', xlabel='Position (Å)', ylabel='Energy (eV)',
                 **kargs):
        super(PlotEPotential, self).__init__(title=title, xlabel=xlabel, ylabel=ylabel, **kargs)
        self.lpotential = LOCPOT(name="LOCPOT").line_potential(direction=direction)

        if output:
            pos, value = self.lpotential
            lpotential2col = np.concatenate((pos.reshape(-1, 1), value.reshape(-1, 1)), axis=1)
            np.savetxt("VLINE", lpotential2col, fmt='%.6f', delimiter="\t")

    @plot_wrapper
    def plot(self):
        """
        Plot Electrostatic Potential
        """
        plt.plot(*self.lpotential)


class PlotCCD(Figure):
    def __init__(self, direction='z', xlabel='Position along z-axis (Å)', ylabel='Charge density (e/Å)', **kargs):
        super(PlotCCD, self).__init__(xlabel=xlabel, ylabel=ylabel, **kargs)
        self.lpotential = CHGCAR_diff(name="CHGCAR_diff").line_potential(direction=direction)

    @plot_wrapper
    def plot(self):
        """
        Plot Charge Density Difference
        """
        plt.plot(*self.lpotential)


class PESData(object):
    """
    Generate the data for PlotPES

    Methods:
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

        Returns:
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

        Returns:
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

    Methods:
        plot():     plot main func

        add_solid:  auxiliary func, add solid line
        add_dash:   auxiliary func, add dash line
        add_text:   auxiliary func, add text
    """

    def __init__(self, width=15.6, height=4, weight='bold', xlabel="Reaction coordinate", ylabel="Energy (eV)",
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
    def plot(self, data, color, text_type=None, style="solid_dash", legend=None):
        """
        Main plot func of <PlotPES class>

        Args:
            data:       energy or (energy, label) types data
            color:      specify which color you want to plot
            text_type:  only affect `solid_dash` type
            style:      specify which style PES you want to plot, default: solid_dash
            legend:     specify the legend, triple element: [x, y, label]
        """
        data = PESData(data)(style=style)

        if style == "solid_dash":
            self._plot_solid_dash(data, color, text_type=text_type)
        elif style == "solid_curve":
            self._plot_solid_curve(data, color)
        else:
            raise NotImplementedError("style should be `solid_dash` or `solid_curve`")

        if legend is not None:
            plt.plot(legend[0], legend[1], color=color, label=rf"{legend[2]}")

    def _plot_solid_dash(self, data, color, text_type):
        for x, y in zip(data.solid_x, data.solid_y):
            self.add_solid(5, x, y, color)
            if y[0] is not None:
                self.add_text(x, [yi + 0.1 for yi in y], '{:.2f}'.format(y[1]), color) if text_type in ["all",
                                                                                                        "solid"] else 0

        for x, y in zip(data.dash_x, data.dash_y):
            self.add_dash(1.5, x, y, color)
            self.add_text(x, y, '{:.2f}'.format(abs(y[1] - y[0])), color) if text_type in ["all", "dash"] else 0

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

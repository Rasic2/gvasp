import time
from collections import defaultdict
from functools import wraps
from itertools import product

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandas import DataFrame
from scipy import interpolate
from scipy.integrate import simps

from figure import Figure, SolidLine, DashLine, Text, plot_wrapper
from file import CONTCAR, DOSCAR, EIGENVAL

pd.set_option('display.max_columns', None)  # show all columns
pd.set_option('display.max_rows', None)  # show all rows

COLUMNS = ['s_up', 's_down', 'py_up', 'py_down', 'pz_up', 'pz_down', 'px_up', 'px_down', 'dxy_up', 'dxy_down', 'dyz_up',
           'dyz_down', 'dz2_up', 'dz2_down', 'dxz_up', 'dxz_down', 'dx2_up', 'dx2_down', 'f1_up', 'f1_down', 'f2_up',
           'f2_down', 'f3_up', 'f3_down', 'f4_up', 'f4_down', 'f5_up', 'f5_down', 'f6_up', 'f6_down', 'f7_up',
           'f7_down']


def interpolated_wrapper(func):
    @wraps(func)
    def wrapper(self):
        for x, y, number in func(self):
            x_arr = np.array(x)
            y_arr = np.array(y)
            x_new = np.linspace(np.min(x_arr), np.max(x_arr), len(x) * 100)
            f = interpolate.interp1d(x_arr, y_arr, kind='cubic')
            y_new = f(x_new)

            if not self.avgflag:
                number = 1

            if self.method == 'fill':
                plt.fill(x_new, y_new / number, color=self.color)
            elif self.method == 'line':
                plt.plot(x_new, y_new / number, color=self.color)
            elif self.method == 'dash line':
                plt.plot(x_new, y_new / number, '--', color=self.color)
            elif self.method == 'output':
                time_prefix = time.strftime("%H-%M-%S", time.localtime())
                np.savetxt(f"datafile_x_{time_prefix}", x_new)
                np.savetxt(f"datafile_y_{time_prefix}", y_new)

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

    def __init__(self, dos_file, pos_file, max_orbital='f', xlabel="Energy (EV)", ylabel="Density of States (a.u.)",
                 **kargs):
        super(PlotDOS, self).__init__(xlabel=xlabel, ylabel=ylabel, **kargs)
        self.dos_file = dos_file
        self.pos_file = pos_file
        self.max_orbital = max_orbital  # whether you need to plot the f-orbital, default: True
        self.element = PlotDOS.contcar_parse(self.pos_file)
        self.total_dos, self.atom_list = PlotDOS.doscar_parse(self.dos_file)

    @plot_wrapper
    def plot(self, atoms=None, orbitals=None, color="#000000", method='line', avgflag=False):
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
        self.color = color
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

        """Main Content of Plot func"""
        if self.atoms is None:
            return plot_tot(self)

        elif isinstance(self.atoms, list):
            assert all([isinstance(item, int) for item in self.atoms]), f"Atoms must be a Int List!"
            return plot_atoms(self)

        elif isinstance(self.atoms, str):
            if '-' in self.atoms:
                pre_atom = [int(item) for item in self.atoms.split('-')]
                self.atoms = list(range(pre_atom[0], pre_atom[1] + 1, 1))
            else:
                self.atoms = [index for index, element in enumerate(self.element) if self.atoms == element]
                assert len(self.atoms) > 0, f"Atoms don't have this element!"
            return plot_atoms(self)

        elif isinstance(self.atoms, int):
            self.atoms = [self.atoms]
            return plot_atoms(self)

        else:
            raise ValueError(f"The format of {self.atoms} is not correct!")

    def center(self, atoms=None, orbitals=None, xlim=None):
        """Calculate Band-Center Value"""

        old_atoms = atoms
        if isinstance(old_atoms, str):
            if '-' in old_atoms:
                pre_atom = [int(item) for item in old_atoms.split('-')]
                atoms = list(range(pre_atom[0], pre_atom[1] + 1, 1))
            else:
                atoms = [index for index, element in enumerate(self.element) if old_atoms == element]
                print(atoms)

        y = 0
        rang = (self.total_dos.index.values < xlim[1]) & (self.total_dos.index.values > xlim[0])
        if atoms is None:
            y += self.total_dos.loc[rang, 'tot_up']
            y -= self.total_dos.loc[rang, 'tot_down']
        elif orbitals is not None:
            for atom in atoms:
                for orbital in orbitals:
                    y += self.atom_list[atom].loc[rang, '{}_up'.format(orbital)]
                    y -= self.atom_list[atom].loc[rang, '{}_down'.format(orbital)]
        else:
            for atom in atoms:
                y += self.atom_list[atom].loc[rang, 'up']
                y -= self.atom_list[atom].loc[rang, 'down']
        e_count = simps(y.values, y.index.values)  # Simpson Integration method for obtain the electrons' num
        dos = simps([a * b for a, b in zip(y.values, y.index.values)], y.index.values)
        print("Number of Electrons: {0:.4f}; Center Value: {1:.4f}".format(e_count, dos / e_count))

    @staticmethod
    def contcar_parse(name):
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
    def doscar_parse(name):
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


class PlotBand(Figure):
    def __init__(self, name, title='Band Structure', **kargs):
        super(PlotBand, self).__init__(title=title, **kargs)
        self.name = name
        self.energy = EIGENVAL(self.name).load().energy

    @plot_wrapper
    def plot(self):
        """
        Plot Band Structure, for spin-system, the average energy was applied
        """
        energy_avg = self.energy.mean(axis=-1)
        for band_index in range(energy_avg.shape[1]):
            plt.plot(energy_avg[:, band_index])


class PESData(object):
    def __init__(self, data):
        self.data = data

    def __call__(self, *args, **kwargs):
        self.solid_x, self.solid_y, self.dash_x, self.dash_y = self.convert()
        return self

    def convert(self):
        solid_x = [[0.75 + 2 * i, 1.25 + 2 * i] for i in range(len(self.data))]
        solid_y = [[value, value] for value in self.data]
        real_index = [index for index, value in enumerate(self.data) if value is not None]
        dash_x_1 = [2 * index + 1.25 for index in real_index[:-1]]
        dash_x_2 = [2 * index + 0.75 for index in real_index[1:]]
        dash_x = [item for item in zip(dash_x_1, dash_x_2)]
        dash_y = [[self.data[int((index[0] - 1.25) / 2)], self.data[int((index[1] - 2.75) / 2 + 1)]] for index in
                  dash_x]
        return solid_x, solid_y, dash_x, dash_y


class PlotPES(Figure):

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

    def add_text(self, x, y, text, color):
        self.texts[color].append(Text(self, x, y, text, color))

    @plot_wrapper
    def plot(self, data, color, option='default'):
        data = PESData(data)()

        for x, y in zip(data.solid_x, data.solid_y):
            self.add_solid(5, x, y, color)

        for x, y in zip(data.dash_x, data.dash_y):
            self.add_dash(1.5, x, y, color)
            self.add_text(x, y, '{:.2f}'.format(abs(y[1] - y[0])), color) if option == 'default' else 0

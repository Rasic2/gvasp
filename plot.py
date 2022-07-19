#!/usr/bin/env python
import glob
import math
import time
from collections import defaultdict
from functools import wraps
from itertools import product

import numpy as np
import pandas as pd
from file import CONTCAR, DOSCAR
from matplotlib import pyplot as plt
from pandas import DataFrame
from scipy import interpolate
from scipy.integrate import simps

pd.set_option('display.max_columns', None)  # show all columns
pd.set_option('display.max_rows', None)  # show all rows

ORBITALS = ['s', 'p', 'd', 'f']
COLUMNS = ['s_up', 's_down', 'py_up', 'py_down', 'pz_up', 'pz_down', 'px_up', 'px_down', 'dxy_up', 'dxy_down', 'dyz_up',
           'dyz_down', 'dz2_up', 'dz2_down', 'dxz_up', 'dxz_down', 'dx2_up', 'dx2_down', 'f1_up', 'f1_down', 'f2_up',
           'f2_down', 'f3_up', 'f3_down', 'f4_up', 'f4_down', 'f5_up', 'f5_down', 'f6_up', 'f6_down', 'f7_up',
           'f7_down']


def plot_wrapper(func):
    @wraps(func)
    def wrapper(self, *args, **kargs):
        plt.rc('font', family='DejaVu Sans')  # set the font globally
        plt.rcParams['mathtext.default'] = 'regular'  # set the math-font globally
        plt.rcParams['lines.linewidth'] = 2  # set line-width
        plt.rcParams['lines.color'] = kargs['color']  # set line-color
        func(self, *args, **kargs)
        plt.xlim((self.atom_list[0][0], self.atom_list[0][-1])) if self.xlim == None else plt.xlim(self.xlim)
        plt.xticks(fontsize=26)
        plt.yticks(fontsize=26)
        plt.xlabel('Energy (eV)', fontsize=28)
        plt.ylabel('Density of States (a.u.)', fontsize=28)

    return wrapper


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


class PlotDOS(object):
    """
    <PlotDOS main class>

    @method:
        plot():     plot main func
        center():   calculate the band-center

    @static-method:
        contcar_parse:  parse CONTCAR data
        doscar_parse:   parse DOSCAR data
    """

    def __init__(self, DOSCAR, CONTCAR, max_orbital='f'):
        self.DOSCAR = DOSCAR
        self.CONTCAR = CONTCAR
        self.max_orbital = max_orbital  # whether you need to plot the f-orbital, default: True
        self.element = PlotDOS.contcar_parse(self.CONTCAR)
        self.total_dos, self.atom_list = PlotDOS.doscar_parse(self.DOSCAR)

    @plot_wrapper
    def plot(self, atoms=None, orbitals=None, xlim=None, color='', method='fill', avgflag=False):
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
        self.xlim = xlim
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
        e_count = simps(y.values, y.index.values)  # 辛普森积分方法，计算电子数
        dos = simps([a * b for a, b in zip(y.values, y.index.values)], y.index.values)
        print("电子数为: {0:.4f} center值为: {1:.4f}".format(e_count, dos / e_count))

    @staticmethod
    def contcar_parse(name):
        """
        read CONTCAR file, obtain the elements list.

        @params:
            name:       CONTCAR file name

        @return:
            element:    elements list, e.g., ['','Be','Be','C']
        """

        structure = CONTCAR(name=name).to_structure()
        element = [' '] + structure.atoms.formula
        return element

    @staticmethod
    def doscar_parse(name):
        def datatype_convert(energy_list, Total_up, Total_down, atom_list, length):
            atom_data = [energy_list]
            columns = COLUMNS[:length]
            orbitals = ORBITALS[1:int(math.sqrt(length / 2))]
            Total_Dos = DataFrame(index=energy_list, columns=['tot_up', 'tot_down'], dtype='object')
            Total_Dos['tot_up'] = Total_up
            Total_Dos['tot_down'] = Total_down

            for data in atom_list:
                DATA = DataFrame(data, index=energy_list, columns=columns)
                DATA['up'] = 0.0
                DATA['down'] = 0.0
                for orbital in orbitals:
                    DATA[orbital + '_up'] = 0.0
                    DATA[orbital + '_down'] = 0.0
                    orbital_p_up = [item for item in DATA.columns.values if
                                    item.startswith(orbital) and item.endswith('up') and item != '{}_up'.format(
                                        orbital) and item != 'up']
                    orbital_p_down = [item for item in DATA.columns.values if
                                      item.startswith(orbital) and item.endswith('down') and item != '{}_down'.format(
                                          orbital) and item != 'down']
                    for item in orbital_p_up:
                        DATA[f'{orbital}_up'] += DATA[item]
                    for item in orbital_p_down:
                        DATA[f'{orbital}_down'] += DATA[item]
                    DATA['up'] += DATA[f'{orbital}_up']
                    DATA['down'] += DATA[f'{orbital}_down']
                DATA['up'] += DATA['s_up']
                DATA['down'] += DATA['s_down']
                atom_data.append(DATA)
            return Total_Dos, atom_data

        return datatype_convert(*DOSCAR(name=name).load())


if __name__ == '__main__':
    plt.figure(figsize=(10, 8))
    datafiles = glob.glob("datafile*")

    name = 'test'
    DS = [f'DOSCAR-{name}']
    CS = [f'CONTCAR-{name}']

    print("正在加载文件...")
    # with futures.ProcessPoolExecutor() as executor:
    P = map(PlotDOS, DS, CS)
    P = list(P)
    print("文件加载完成...")

    P[0].plot(atoms='Ce', orbitals=None, xlim=[-6, 9], color='#123E09', method='line')

    plt.savefig('figure.svg', dpi=300, bbox_inches='tight', format='svg')

# profile.run('main("")','result')
# p=pstats.Stats("result")
# p.strip_dirs().sort_stats("time").print_stats()

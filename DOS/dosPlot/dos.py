#!/usr/bin/env python

import glob
import math
import os
import time
from collections import defaultdict
from functools import wraps

import numpy as np
import pandas as pd
from c_doscar_load import doscar_load
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
        plt.rcParams['lines.color'] = self.color  # set line-color
        func(self, *args, **kargs)
        plt.xlim((self.atom_list[0][0], self.atom_list[0][-1])) if self.xlim == None else plt.xlim(self.xlim)
        plt.xticks(fontsize=26)
        plt.yticks(fontsize=26)
        plt.xlabel('Energy (eV)', fontsize=28)
        plt.ylabel('Density of States (a.u.)', fontsize=28)

    return wrapper


class PlotDOS():
    """
    <PlotDOS main class>

    @method:
        __load: load DOSCAR、CONTCAR or POSCAR data
        plot(): plot main func
        center: calculate the band-center

    @static-method:
        contcar_parse:  load CONTCAR
        doscar_parse:   load DOSCAR
    """

    def __init__(self, DOSCAR, CONTCAR, max_orbital='f'):
        self.DOSCAR = DOSCAR
        self.CONTCAR = CONTCAR
        self.max_orbital = max_orbital  # whether you need to plot the f-orbital, default: True
        self.element = PlotDOS.contcar_parse(self.CONTCAR)
        self.total_dos, self.atom_list = PlotDOS.doscar_parse(self.DOSCAR)

    def plot(self, xlim=None, show=False, color='', method='fill', **kargs):
        """实例化一个DOS对象
        1、可以指定x坐标范围
        2、指定是否将DOS分别绘制
        """
        DOS(self.total_dos, self.atom_list, self.element, xlim=xlim, show=show, color=color, method=method, **kargs)

    def center(self, atoms=None, orbitals=None, xlim=None):
        """计算DOS 特定原子轨道的center值"""

        old_atoms = atoms
        if isinstance(old_atoms, str):  # modified at 2019/04/20 实现'a-b'代替列表求plot_dos
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
    def contcar_parse(CONTCAR):
        """
        read CONTCAR file, obtain the elements list.

        return:     elements list, e.g., ['','Be','Be','C']
        """
        elem_name, elem_count = os.popen("sed -n '6p' {}".format(CONTCAR)), os.popen("sed -n '7p' {}".format(CONTCAR))
        names = elem_name.read().rstrip().split()
        counts = [int(item) for item in elem_count.read().rstrip().split()]
        result = ['']
        for index, count in enumerate(counts):
            while count != 0:
                result.append(names[index])
                count -= 1
        return result

    @staticmethod
    def doscar_parse(DOSCAR):
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

        return datatype_convert(*doscar_load(DOSCAR))


def interpolated_plot(x, y, number=1, label='', color='', method='', avgflag=False):
    """
    fitting the DOSCAR data
    
    @params:
        method:     control how to plot the dos, ['fill', 'line', 'dash line', 'output']
    """

    count = len(x)
    x_arr = np.array(x)
    y_arr = np.array(y)
    x_new = np.linspace(np.min(x_arr), np.max(x_arr), count * 100)
    f = interpolate.interp1d(x_arr, y_arr, kind='cubic')
    y_new = f(x_new)

    if not avgflag:
        number = 1

    if method == 'fill':
        plt.fill(x_new, y_new / number, label=label, color=color)
    elif method == 'line':
        plt.plot(x_new, y_new / number, label=label, color=color)
    elif method == 'dash line':
        plt.plot(x_new, y_new / number, '--', label=label, color=color)
    elif method == 'output':
        time_prefix = time.strftime("%H-%M-%S", time.localtime())
        np.savetxt(f"datafile_x_{time_prefix}", x_new)
        np.savetxt(f"datafile_y_{time_prefix}", y_new)


class DOS():
    def __init__(self, total_dos, atom_list, element, color, xlim=None, show=False, method=None, avgflag=False,
                 **kargs):
        """
        -->不指定参数, 画TOT_DOS								e.g. DOS()
        -->原子列表, 画原子Plus_DOS							e.g. DOS(atom=[1,2,3])
           --> 指定原子列表, 同时指定轨道, 画该轨道下plus_dos	e.g. DOS(atom=[1,3,4],orbital=['s','p'])
           --> 简化获取连续多原子方法							e.g. DOS(atom='1-3',orbital=['s','p'])
        -->单个原子, 不指定轨道, atom_tot						e.g. DOS(atom=1)
        -->单个原子, 指定轨道, PDOS							e.g. DOS(atom=1,orbital=['s','p'])
        """
        # super().__init__()
        self.total_dos = total_dos
        self.atom_list = atom_list
        self.element = element
        self.atoms = None
        self.orbitals = None
        self.xlim = xlim
        self.kargs = kargs
        self.color = color
        self.method = method
        self.avgflag = avgflag  # modified at 2022/05/07 是否计算平均DOS选项（按原子数）
        for key, value in self.kargs.items():
            setattr(self, key, value)
        self.show = show
        self.plot()
        if self.show == True:
            plt.show()

    @plot_wrapper
    def plot(self):
        """DOS画图函数"""
        if 'atoms' not in self.kargs.keys():
            self.plot_tot()
        elif isinstance(self.kargs['atoms'], list):
            self.plot_atoms()
        elif isinstance(self.kargs['atoms'], str):  # modified at 2019/04/20 实现'a-b'代替列表求plot_dos
            if '-' in self.kargs['atoms']:
                pre_atom = [int(item) for item in self.kargs['atoms'].split('-')]
                setattr(self, 'atoms', list(range(pre_atom[0], pre_atom[1] + 1, 1)))
            else:
                self.atoms = [index for index, element in enumerate(self.element) if self.kargs['atoms'] == element]
            self.plot_atoms()
        elif isinstance(self.atoms, int):
            self.atoms = [self.atoms]
            self.plot_atoms()
        else:
            raise ValueError(f"The format of {self.atoms} is not correct!")

    def plot_tot(self):
        """Plot Total DOS"""
        for column in self.total_dos.columns.values:
            interpolated_plot(self.total_dos.index.values, list(self.total_dos[column].values), label=column,
                              color=self.color, method=self.method)
        plt.legend(loc='best')

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
        if self.orbitals == None:
            interpolated_plot(plus_tot.index.values, plus_tot['up'].values, number=len(self.atoms), color=self.color,
                              method=self.method, avgflag=self.avgflag)
            interpolated_plot(plus_tot.index.values, plus_tot['down'].values, number=len(self.atoms), color=self.color,
                              method=self.method, avgflag=self.avgflag)
        else:
            for orbital in self.orbitals:
                interpolated_plot(plus_tot.index.values, plus_tot[f'{orbital}_up'], number=len(self.atoms),
                                  color=self.color, method=self.method, avgflag=self.avgflag)
                interpolated_plot(plus_tot.index.values, plus_tot[f'{orbital}_down'], number=len(self.atoms),
                                  color=self.color, method=self.method, avgflag=self.avgflag)


def main_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        plt.figure(figsize=(10, 8))
        func(*args, **kargs)
        if args[0] == 'show':
            plt.show()
        elif args[0] == 'save':
            plt.savefig('figure.svg', dpi=300, bbox_inches='tight', format='svg')

    return wrapper


@main_wrapper
def main(option):
    datafiles = glob.glob("datafile*")

    name = 'test'
    DS = [f'DOSCAR-{name}']
    CS = [f'CONTCAR-{name}']

    print("正在加载文件...")
    # with futures.ProcessPoolExecutor() as executor:
    P = map(PlotDOS, DS, CS)
    P = list(P)
    print("文件加载完成...")

    P[0].plot(atoms=1, orbitals=['s'], xlim=[-6, 9], color='#123E09', method='line')


if __name__ == '__main__':
    main('save')
# main('')

# profile.run('main("")','result')
# p=pstats.Stats("result")
# p.strip_dirs().sort_stats("time").print_stats()

import os
import sys
from pathlib import Path


def surface_energy(E_slab, n, E_unit, A):
    """
    Calculate the surface energy

    @params
        E_slab:		total energy of slab
        E_unit:		total energy of one structure unit
        n:			number of structure unit
        A:			area of surface slab

    @return
        E_surf:		surface energy, unit: J/m^2
    """
    E_surf = (E_slab - n * E_unit) / (2 * A) * 16.02
    return E_surf


def colors_generator():
    """
    Color cycle generator
    """
    while True:
        yield from ['#000000', '#01545a', '#ed0345', '#ef6932', '#710162', '#017351', '#03c383', '#aad962', '#fbbf45',
                    '#a12a5e']


def get_HOME() -> Path:
    """
    obtain HOME directory
    """
    if sys.platform == 'win32':
        home_dir = os.environ['USERPROFILE']
    elif sys.platform == 'linux' or sys.platform == 'darwin':
        home_dir = os.environ['HOME']
    else:
        raise NotImplemented(f"Can't identify the HOME directory of {sys.platform} platform!")
    return Path(home_dir)

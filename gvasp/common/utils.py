import logging
import os
import sys
from pathlib import Path

import numpy as np
from pandas import Series

from common.constant import RecommendPot

logger = logging.getLogger(__name__)


def colors_generator():
    """
    Color cycle generator
    """
    while True:
        yield from ['#000000', '#01545a', '#ed0345', '#ef6932', '#710162', '#017351', '#03c383', '#aad962', '#fbbf45',
                    '#a12a5e', '#047df6', '#FFFF33', '#F1D1E1', '#E6FFE7']


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


def identify_atoms(atoms, elements):
    """Calculate the real index for the atoms"""
    if not isinstance(atoms, list):
        atoms = [atoms]

    inner_atoms = []
    for item in atoms:
        if isinstance(item, int):
            inner_atoms.append(item)
        elif isinstance(item, str):
            if '-' in item:
                slice_atoms = [int(item) for item in item.split('-')]
                if slice_atoms[1] >= len(elements):
                    logger.error(f"The end index `{slice_atoms[1]}` > atoms count ({len(elements) - 1})")
                    exit(1)
                inner_atoms += list(range(slice_atoms[0], slice_atoms[1] + 1, 1))
            else:
                element_atoms = [index for index, element in enumerate(elements) if item == element]
                if len(element_atoms) == 0:
                    logger.warning(f"Atoms don't have <Element {item}>, ignore it!")
                inner_atoms += element_atoms
        else:
            raise TypeError(f"The format of {atoms} is not correct!")

    set_atoms = set(inner_atoms)
    if len(inner_atoms) != len(set_atoms):
        logger.warning("The specification of atoms have repeat items, we will only use once for it!")

    return list(set_atoms)


def search_peak(dos_data: Series, tol: float = 0.0001):
    extremes = []
    for index, value in enumerate(dos_data):
        if 0 < index < len(dos_data) - 1:
            before_value = dos_data.values[index - 1]
            after_value = dos_data.values[index + 1]
            if value > before_value + tol and value > after_value + tol:
                extremes.append(index)
    energy_extremes = dos_data.index[extremes].values
    return energy_extremes


def remove_mapping(atoms: list, tol=0.01):
    identity_atoms = []
    for atom in atoms:
        if not len(identity_atoms):
            identity_atoms.append(atom)
        else:
            for eatom in identity_atoms:
                if atom[0] == eatom[0]:
                    diff = np.array(atom[1]) - np.array(eatom[1])
                    diff = np.where(diff == 1.0, 0., diff)
                    diff = np.where(diff == -1.0, 0., diff)
                    if np.sum(np.abs(diff)) <= tol:
                        break
            else:
                identity_atoms.append(atom)
        pass

    return identity_atoms


def is_subset_recommend_pot(element):
    """
    Identify an element is or not in RecommendPot
    """
    for key, value in RecommendPot.items():
        if element in value:
            return key
    else:
        return False

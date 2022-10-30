from pathlib import Path

import numpy as np

from gvasp.common.constant import RESET, GREEN, RED
from gvasp.common.utils import identify_atoms
from gvasp.common.file import OUTCAR, POSCAR, POTCAR, ACFFile


def surface_energy(crystal_dir: str, slab_dir: str):
    """
    Calculate the surface energy

    Args:
        crystal_dir (str): crystal calculation job directory
        slab_dir (str): slab calculation job directory

    Returns:
        E_surf:		surface energy, unit: J/m^2
    """
    crystal_outcar = OUTCAR(Path(crystal_dir) / "OUTCAR")
    slab_outcar = OUTCAR(Path(slab_dir) / "OUTCAR")

    E_crystal = crystal_outcar.last_energy
    E_slab = slab_outcar.last_energy

    N_crystal = crystal_outcar.element
    N_slab = slab_outcar.element

    lattice_slab = slab_outcar.lattice

    n = N_slab / N_crystal
    A = lattice_slab.length[0] * lattice_slab.length[1]

    E_surf = (E_slab - n * E_crystal) / (2 * A) * 16.02

    print(f"The surface energy: {E_surf}")
    return E_surf


def electrostatic_energy(atoms, workdir="."):
    structure = POSCAR(Path(workdir) / "CONTCAR").structure
    potcar = POTCAR(Path(workdir) / "POTCAR")
    atom_valence = np.array([potcar.valence[potcar.element.index(atom.formula)] for atom in structure.atoms])
    acf = ACFFile("ACF.dat")
    atom_charge = atom_valence - acf.charge
    structure.find_neighbour_table(neighbour_num=None, cut_radius=3.)
    neighbour_table = structure.neighbour_table

    if isinstance(atoms, (list, int, str)):
        atoms = identify_atoms(atoms, [""] + structure.atoms.formula)

    E_static = []
    print("| atom_i | atom_j | i_charge | j_charge | distance | E_static |")
    for atom in atoms:
        pair_order, pair_distance = list(
            map(list, zip(*[(item[0].order, item[1]) for item in neighbour_table[structure.atoms[atom - 1]]])))
        pair_charge = [(atom_charge[atom - 1], atom_charge[order]) for order in pair_order]

        print("-".center(63, "-"))
        E_static_inner = []
        for order, (i_charge, j_charge), distance in zip(pair_order, pair_charge, pair_distance):
            e_static = i_charge * j_charge / distance
            print(
                f"| {atom:>6d} | {order + 1:>6d} | {i_charge:+8.5f} | {j_charge:+8.5f} | {distance:8.6f} | {e_static:+8.5f} |")
            E_static_inner.append(e_static)
            E_static.append(e_static)
        print(f"{GREEN}Atom Electrostatic Energy: {sum(E_static_inner):+8.5f} e^2/Å{RESET}".rjust(74))
    print("-".center(63, "-"))
    print(f"\n{RED}Total Electrostatic Energy: {sum(E_static):+8.5f} e^2/Å.{RESET}")

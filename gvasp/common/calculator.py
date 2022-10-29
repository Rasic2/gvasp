from pathlib import Path

from gvasp.common.file import OUTCAR


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
    return E_surf

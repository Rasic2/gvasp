import math
from pathlib import Path

import numpy as np
from scipy import constants

from gvasp.common.constant import RESET, GREEN, RED
from gvasp.common.file import OUTCAR, POSCAR, POTCAR, ACFFile
from gvasp.common.utils import identify_atoms


def surface_energy(crystal_dir: str, slab_dir: str):
    """
    Calculate the surface energy

    Args:
        crystal_dir (str): crystal calculation job directory
        slab_dir (str): slab calculation job directory

    Returns:
        E_surf:		surface energy, unit: J/m^2
    """
    crystal_outcar = OUTCAR(Path(crystal_dir) / 'OUTCAR')
    slab_outcar = OUTCAR(Path(slab_dir) / 'OUTCAR')

    E_crystal = crystal_outcar.last_energy
    E_slab = slab_outcar.last_energy

    N_crystal = crystal_outcar.element
    N_slab = slab_outcar.element

    lattice_slab = slab_outcar.lattice

    n = N_slab / N_crystal
    A = lattice_slab.length[0] * lattice_slab.length[1]

    E_surf = (E_slab - n * E_crystal) / (2 * A) * 16.02

    print(f'The surface energy: {E_surf}')
    return E_surf


def electrostatic_energy(atoms, workdir='.'):
    structure = POSCAR(Path(workdir) / 'CONTCAR').structure
    potcar = POTCAR(Path(workdir) / 'POTCAR')
    atom_valence = np.array([potcar.valence[potcar.element.index(atom.formula)] for atom in structure.atoms])
    acf = ACFFile('ACF.dat')
    atom_charge = atom_valence - acf.charge
    structure.find_neighbour_table(neighbour_num=None, cut_radius=3.)
    neighbour_table = structure.neighbour_table

    if isinstance(atoms, (list, int, str)):
        atoms = identify_atoms(atoms, [''] + structure.atoms.formula)

    E_static = []
    print('| atom_i | atom_j | i_charge | j_charge | distance | E_static |')
    for atom in atoms:
        pair_order, pair_distance = list(
            map(list, zip(*[(item[0].order, item[1]) for item in neighbour_table[structure.atoms[atom - 1]]])))
        pair_charge = [(atom_charge[atom - 1], atom_charge[order]) for order in pair_order]

        print('-'.center(63, '-'))
        E_static_inner = []
        for order, (i_charge, j_charge), distance in zip(pair_order, pair_charge, pair_distance):
            e_static = i_charge * j_charge / distance
            print(
                f'| {atom:>6d} | {order + 1:>6d} | {i_charge:+8.5f} | {j_charge:+8.5f} | {distance:8.6f} | {e_static:+8.5f} |')
            E_static_inner.append(e_static)
            E_static.append(e_static)
        print(f'{GREEN}Atom Electrostatic Energy: {sum(E_static_inner):+8.5f} e^2/Å{RESET}'.rjust(74))
    print('-'.center(63, '-'))
    print(f'\n{RED}Total Electrostatic Energy: {sum(E_static):+8.5f} e^2/Å.{RESET}')


h_p = constants.h  # Plank Constant: 6.62606957E-34 J*s
k_b = constants.k  # Boltzmann Constant: 1.38064852E-23 m²*kg*s⁻²*K⁻¹
R_gas = constants.R  # Gas Constant: 8.3144598 J*mol⁻¹*K⁻¹
l_s = constants.c  # Light Speed: 299792458 m * s ⁻¹


def thermo_adsorbent(temperature: float = 298.15):
    beta = 1 / (k_b * temperature)

    def partition_function(miu):
        x_i = h_p * float(miu) * l_s * beta  # hv/kT
        pf_l = x_i / (math.exp(x_i) - 1)  # (hv/kT)/(e^(hv/kT) -1 )
        pf_r = math.log(1 - math.exp(-x_i))  # ln(1-e^(-hv/kT))
        pf = pf_l - pf_r
        enthalpy = R_gas * pf_l * temperature
        entropy = R_gas * pf
        return enthalpy, entropy

    frequency = OUTCAR('OUTCAR').frequency
    w_number_list, v_energy_list = list(map(list,
                                            zip(*[(frequency.wave_number[index], frequency.vib_energy[index])
                                                  for index, freq in enumerate(frequency.image) if not freq])))

    E_zpe = sum(v_energy_list) / 2 / 1000  # calculate ZPE: (1) Sum(hv)/2  (2) convert meV to eV

    H_vib = sum(partition_function(i * 100)[0] for i in w_number_list)  # i* 100: cm-1 -> m-1
    S_vib = sum(partition_function(max(i, 50) * 100)[1] for i in w_number_list)  # if i <= 50 cm-1, let i=50

    H_tot = H_vib / 1000 / 96.485 + E_zpe  # convert J * mol⁻¹ to eV
    S_tot = S_vib / 1000 / 96.485  # convert J * K⁻¹ * mol⁻¹ to eV * K⁻¹
    TS_tot = temperature * S_tot
    G_tot = H_tot - TS_tot

    E_DFT = OUTCAR('OUTCAR').last_energy
    G = E_DFT + G_tot

    print('+' + '-'.center(55, '-') + '+')
    print('|' + f'Thermo Correction for adsorbent (T = {temperature:.2f} K)'.center(55, ' ') + '|')
    print('|' + '-'.center(55, '-') + '|')
    print('|' + f' Zero-point energy E_ZPE'.ljust(30, ' ') + f': {E_zpe:10.7f} eV'.ljust(25, ' ') + '|')
    print('|' + f' Thermal correction to H(T)'.ljust(30, ' ') + f': {H_tot:10.7f} eV'.ljust(25, ' ') + '|')
    print('|' + f' Thermal correction to G(T)'.ljust(30, ' ') + f': {G_tot:10.7f} eV'.ljust(25, ' ') + '|')
    print('|' + f' Entropy S'.ljust(30, ' ') + f': {S_tot:10.7f} eV/K'.ljust(25, ' ') + '|')
    print('|' + f' Entropy contribution T*S'.ljust(30, ' ') + f': {TS_tot:10.7f} eV'.ljust(25, ' ') + '|')
    print('+' + f'-'.center(55, '-') + '+')
    print('|' + f' DFT energy E_DFT'.ljust(30, ' ') + f': {E_DFT:10.4f} eV'.ljust(25, ' ') + '|')
    print('|' + f' Gibbs Free Energy G(T)'.ljust(30, ' ') + f': {G:10.4f} eV'.ljust(25, ' ') + '|')
    print('+' + '-'.center(55, '-') + '+')


def thermo_gas(temperature=298.15, pressure=1, multiplicity=1):
    """Development in future"""
    beta = 1 / (k_b * temperature)

    def partition_function(miu):
        x_i = h_p * float(miu) * l_s * beta  # hv/kT
        pf_l = x_i * math.exp(-x_i) / (1 - math.exp(-x_i))  # (hv/kT)*(e^(-hv/kT))/(1-e^(-hv/kT))
        pf_r = math.log(1 - math.exp(-x_i))  # ln(1-e^(-hv/kT))
        pf = pf_l - pf_r
        enthalpy = R_gas * pf_l * temperature
        entropy = R_gas * pf
        return enthalpy, entropy

    outcar = OUTCAR('OUTCAR')
    frequency = outcar.frequency
    w_number_list, v_energy_list = list(map(list,
                                            zip(*[(frequency.wave_number[index], frequency.vib_energy[index])
                                                  for index, freq in enumerate(frequency.image) if not freq])))
    image_count = sum(frequency.image)
    E_zpe = sum(sorted(v_energy_list, reverse=True)[:len(v_energy_list) - 6 + image_count]) / 2 / 1000  # no-linear mol
    real_vib_w_number = sorted(w_number_list, reverse=True)[:len(w_number_list) - 6 + image_count]

    H_trans = 2.5 * R_gas * temperature
    H_rot = 1.5 * R_gas * temperature  # no-linear mol
    H_vib = sum(partition_function(i * 100)[0] for i in real_vib_w_number)
    H_tot = (H_trans + H_rot + H_vib) / 1000 / 96.485 + E_zpe

    print('+' + '-'.center(55, '-') + '+')
    print('|' + f'Thermo Correction for adsorbent'.center(55, ' ') + '|')
    print('|' + f'Condition: T = {temperature:.2f} K, P = {pressure:.2f} atm, I = {multiplicity:2d}'.center(55,
                                                                                                            ' ') + '|')
    print('|' + '-'.center(55, '-') + '|')
    print('|' + f' Zero-point energy E_ZPE'.ljust(30, ' ') + f': {E_zpe:10.7f} eV'.ljust(25, ' ') + '|')
    print('|' + f' Thermal correction to H(T)'.ljust(30, ' ') + f': {H_tot:10.7f} eV'.ljust(25, ' ') + '|')
    print('+' + '-'.center(55, '-') + '+')

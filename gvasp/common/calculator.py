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

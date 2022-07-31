from common.structure import Structure

structure = Structure.from_POSCAR("POSCAR")
structure.atoms.perturb(structure.lattice, threshold=0.1)
structure.write_POSCAR("POSCAR_perturb")

from file import POSCAR

POSCAR.align("POSCAR_IS", "POSCAR_FS")
# structure = POSCAR("POSCAR_IS").structure
# structure.find_neighbour_table()
# atoms = POSCAR("IS").structure.atoms
# image = atoms.search_image(atoms, atoms)
print()
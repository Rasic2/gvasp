from common.structure import Structure

def from_cell():
    structure = Structure.from_cell("test.cell")

def fixed():
    structure = Structure.from_POSCAR("POSCAR_IS")
    atoms = structure.atoms
    print(atoms.selective_matrix[0])
    atoms.selective_matrix[0] = ['F', 'F', 'T']
    print(atoms.selective_matrix[0])
    print()

if __name__ == '__main__':
    fixed()
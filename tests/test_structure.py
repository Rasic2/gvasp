import line_profiler

from common.base import Atom
from common.file import POSCAR
from common.structure import Structure


def main():
    structure = POSCAR("POSCAR_IS_sort").structure
    structure.find_neighbour_table(neighbour_num=structure.atoms.count, sort=False, including_self=True)


if __name__ == '__main__':
    profile = line_profiler.LineProfiler()
    profile.add_function(Atom.set_coord)
    profile.add_function(Structure.find_neighbour_table)
    profile.add_function(Atom.search_image)
    profile_wrapper = profile(main)
    profile_wrapper()
    profile.print_stats()

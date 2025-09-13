import unittest
from pathlib import Path

from gvasp.common.setting import RootDir
from gvasp.common.file import POSCAR


class TestStructure(unittest.TestCase):
    def test_structure(self):
        structure = POSCAR(f'{Path(RootDir).parent}/tests/POSCAR_IS_sort').structure
        structure.find_neighbour_table(neighbour_num=structure.atoms.count, sort=False, including_self=True)


if __name__ == '__main__':
    unittest.main()

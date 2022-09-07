import unittest
from pathlib import Path

from gvasp.common.file import POSCAR
from gvasp.common.setting import RootDir


class TestAlign(unittest.TestCase):
    def test_align(self):
        POSCAR.align(f"{Path(RootDir).parent}/tests/POSCAR_IS", f"{Path(RootDir).parent}/tests/POSCAR_FS")


if __name__ == '__main__':
    unittest.main()
